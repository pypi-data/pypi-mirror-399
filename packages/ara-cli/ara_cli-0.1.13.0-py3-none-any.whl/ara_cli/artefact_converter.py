import os
import logging
from ara_cli.prompt_handler import LLMSingleton
from langfuse.api.resources.commons.errors import Error as LangfuseError, NotFoundError
from ara_cli.classifier import Classifier
from ara_cli.artefact_reader import ArtefactReader
from ara_cli.artefact_creator import ArtefactCreator
from ara_cli.error_handler import AraError
from ara_cli.directory_navigator import DirectoryNavigator
from ara_cli.artefact_deleter import ArtefactDeleter


class AraArtefactConverter:
    def __init__(self, file_system=None):
        self.file_system = file_system or os
        self.reader = ArtefactReader()
        self.creator = ArtefactCreator(self.file_system)

    def convert(
        self,
        old_classifier: str,
        artefact_name: str,
        new_classifier: str,
        merge: bool = False,
        override: bool = False,
    ):
        try:
            self._validate_classifiers(old_classifier, new_classifier)

            content, artefact_info = self.reader.read_artefact_data(
                artefact_name, old_classifier
            )
            if not content or not artefact_info:
                raise AraError(
                    f"Artefact '{artefact_name}' of type '{old_classifier}' not found"
                )

            target_content_existing = self._resolve_target_content(
                artefact_name, new_classifier, merge, override
            )

            target_class = self._get_target_class(new_classifier)

            prompt = self._get_prompt(
                old_classifier=old_classifier,
                new_classifier=new_classifier,
                artefact_name=artefact_name,
                content=content,
                target_content_existing=target_content_existing,
                merge=merge,
            )

            print(
                f"{'Merging' if merge and target_content_existing else 'Converting'} '{artefact_name}' from {old_classifier} to {new_classifier}..."
            )

            converted_artefact = self._run_conversion_agent(prompt, target_class)
            artefact_content = converted_artefact.serialize()

            self._write_artefact(
                new_classifier,
                artefact_name,
                artefact_content,
                merge=merge,
                override=override,
            )

            if old_classifier != new_classifier:
                self._move_data_folder_content(
                    old_classifier, new_classifier, artefact_name
                )
                deleter = ArtefactDeleter(self.file_system)
                deleter.delete(artefact_name, old_classifier, force=True)

        except ValueError as e:
            raise e
        except AraError as e:
            raise e
        except Exception as e:
            raise e

    def _validate_classifiers(self, old_classifier: str, new_classifier: str):
        if not Classifier.is_valid_classifier(old_classifier):
            raise ValueError(f"Invalid classifier: {old_classifier}")
        if not Classifier.is_valid_classifier(new_classifier):
            raise ValueError(f"Invalid classifier: {new_classifier}")

    def _move_data_folder_content(self, old_classifier, new_classifier, artefact_name):
        import shutil

        navigator = DirectoryNavigator()
        navigator.navigate_to_target()

        sub_directory_old = Classifier.get_sub_directory(old_classifier)
        dir_path_old = self.file_system.path.join(
            sub_directory_old, f"{artefact_name}.data"
        )

        sub_directory_new = Classifier.get_sub_directory(new_classifier)
        dir_path_new = self.file_system.path.join(
            sub_directory_new, f"{artefact_name}.data"
        )

        if self.file_system.path.exists(dir_path_old):
            backup_folder_name = f"{artefact_name}.data.old"
            destination_path = self.file_system.path.join(
                dir_path_new, backup_folder_name
            )

            if not self.file_system.path.exists(dir_path_new):
                os.makedirs(dir_path_new, exist_ok=True)

            if self.file_system.path.exists(destination_path):
                shutil.rmtree(destination_path)

            try:
                shutil.move(dir_path_old, destination_path)
                print(f"Moved old data to {destination_path}")
            except Exception as e:
                print(f"Error moving data directory: {e}")

    def _resolve_target_content(
        self, artefact_name: str, new_classifier: str, merge: bool, override: bool
    ):
        target_content_existing = None
        if not merge and not override:
            _, new_artefact_info = self.reader.read_artefact_data(
                artefact_name, new_classifier
            )
            if new_artefact_info:
                raise ValueError(
                    f"Found already exiting {new_classifier} {artefact_name}. Rerun the command with --override or --merge."
                )
        elif merge:
            target_content_existing, _ = self.reader.read_artefact_data(
                artefact_name, new_classifier
            )
        return target_content_existing

    def _get_target_class(self, new_classifier: str):
        from ara_cli.artefact_models.artefact_mapping import artefact_type_mapping
        from ara_cli.artefact_models.artefact_model import ArtefactType

        target_type = ArtefactType(new_classifier)
        target_class = artefact_type_mapping.get(target_type)

        if not target_class:
            raise AraError(f"No artefact class found for classifier: {new_classifier}")
        return target_class

    def _get_prompt(
        self,
        old_classifier,
        new_classifier,
        artefact_name,
        content,
        target_content_existing,
        merge,
    ):
        try:
            langfuse = LLMSingleton.get_instance().langfuse
            if langfuse is None:
                # This mimics the behavior if authentication failed or env vars missing in Singleton
                raise Exception("Langfuse not initialized in Singleton")

            if merge and target_content_existing:
                prompt_template = langfuse.get_prompt("ara-cli/artefact-convert/merge")
                return prompt_template.compile(
                    old_classifier=old_classifier,
                    new_classifier=new_classifier,
                    artefact_name=artefact_name,
                    content=content,
                    target_content_existing=target_content_existing,
                )
            else:
                prompt_template = langfuse.get_prompt(
                    "ara-cli/artefact-convert/default"
                )
                return prompt_template.compile(
                    old_classifier=old_classifier,
                    new_classifier=new_classifier,
                    artefact_name=artefact_name,
                    content=content,
                )

        except (LangfuseError, NotFoundError, Exception) as e:
            logging.info(f"Could not fetch Langfuse prompt: {e}. Using fallback.")
            # Fallback prompts
            formatting_instructions = (
                "### Data Extraction Rules:\n"
                "- **Users**: Extract usernames ONLY. Do NOT add '@' or 'user_' prefixes. "
                "The system adds these automatically. (e.g., return 'hans', NOT '@user_hans').\n"
                "- **Author**: Extract the author as 'creator_<name>'. Do NOT add the '@' symbol. "
                "(e.g., return 'creator_unknown', NOT '@creator_unknown').\n"
                f"- **Artefact Name**: Use strictly '{artefact_name}'.\n"
                "- **Content**: Adapt the content to the target schema fields."
            )

            if merge and target_content_existing:
                return (
                    f"Merge the following {old_classifier} artefact into the existing {new_classifier} artefact. "
                    "Combine the information from both, prioritizing the structure of the target artefact schema. "
                    "Ensure no critical information is lost. "
                    "\n\n"
                    f"{formatting_instructions}"
                    "\n\n"
                    f"Source Artefact ({old_classifier}):\n```\n{content}\n```"
                    f"\n\nTarget Artefact ({new_classifier}):\n```\n{target_content_existing}\n```"
                )
            else:
                return (
                    f"Convert the following {old_classifier} artefact to a {new_classifier} artefact. "
                    "Preserve the core meaning, business value, and description. "
                    "Map the content to the fields required by the target schema. "
                    "\n\n"
                    f"{formatting_instructions}"
                    "\n\n"
                    f"Source Artefact Content:\n```\n{content}\n```"
                )

    def _run_conversion_agent(self, prompt, target_class):
        from ara_cli.llm_utils import create_pydantic_ai_agent

        agent = create_pydantic_ai_agent(output_type=target_class, instrument=True)
        try:
            result = agent.run_sync(prompt)
            return result.output
        except Exception as e:
            raise AraError(f"LLM conversion failed: {e}")

    def _write_artefact(
        self, new_classifier, artefact_name, artefact_content, merge, override
    ):
        from shutil import rmtree

        navigator = DirectoryNavigator()
        navigator.navigate_to_target()

        sub_directory = Classifier.get_sub_directory(new_classifier)
        file_path = self.file_system.path.join(
            sub_directory, f"{artefact_name}.{new_classifier}"
        )
        dir_path = self.file_system.path.join(sub_directory, f"{artefact_name}.data")

        if self.file_system.path.exists(file_path) and not (override or merge):
            raise ValueError(f"Target file {file_path} already exists.")

        if not merge:
            rmtree(dir_path, ignore_errors=True)

        os.makedirs(dir_path, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(artefact_content)

        print(f"Conversion successful. Created: {file_path}")
