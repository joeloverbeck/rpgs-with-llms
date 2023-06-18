"""This module contains the definition of a CharacterSummaryCreator, that handles creating and saving to a file
the character summary for any given character.
"""
import os
from datetime import datetime

from defines.defines import (
    GPT_3_5,
    GPT_4,
    SYSTEM_ROLE,
    USER_ROLE,
)
from llms.api_requests import request_ai_response_with_functions
from llms.messages import (
    get_message_from_gpt_response,
    load_arguments_of_message_with_function_call,
)
from memories.memories_database_loader import MemoriesDatabaseLoader
from memories.memories_database_querier import MemoriesDatabaseQuerier

from paths.full_paths import (
    get_base_memories_full_path,
    get_character_summary_full_path,
)

CHARACTER_AGE_DETERMINER_GPT_SYSTEM_CONTENT = "I am CharacterAgeDeterminerGPT. I have the responsibility of extracting the age of a character from a list of memories."
GET_CHARACTER_AGE_FUNCTION_NAME = "get_character_age"
GET_CHARACTER_AGE_FUNCTION_DESCRIPTION = "Gets the character's numerical age from a list of memories belonging to that character."
AGE_PARAMETER_NAME = "age"
AGE_PARAMETER_DESCRIPTION = "The numerical age of the character."

CHARACTER_CORE_CHARACTERISTICS_GPT_SYSTEM_CONTENT = "I am CharacterCoreCharacteristicsDeterminerGPT. I have the responsibility of describing a character's core "
CHARACTER_CORE_CHARACTERISTICS_GPT_SYSTEM_CONTENT += (
    "characteristics given a list of that character's memories."
)
GET_CHARACTER_CORE_CHARACTERISTICS_FUNCTION_NAME = "get_character_core_characteristics"
GET_CHARACTER_CORE_CHARACTERISTICS_FUNCTION_DESCRIPTION = "Gets a character's core characteristics from a list of memories belonging to that character."
CORE_CHARACTERISTICS_PARAMETER_NAME = "core_characteristics"
CORE_CHARACTERISTICS_PARAMETER_DESCRIPTION = "The description of the core characteristics of the character, written in natural English."

CHARACTER_DAILY_OCCUPATION_GPT_SYSTEM_CONTENT = "I am CharacterCurrentDailyOccupationDeterminerGPT. I have the responsibility of describing a character's current "
CHARACTER_DAILY_OCCUPATION_GPT_SYSTEM_CONTENT += (
    "daily occupation given a list of that character's memories."
)
GET_CHARACTER_DAILY_OCCUPATION_FUNCTION_NAME = "get_character_daily_occupation"
GET_CHARACTER_DAILY_OCCUPATION_FUNCTION_DESCRIPTION = "Gets a character's current daily occupation from a list of memories belonging to that character."
DAILY_OCCUPATION_PARAMETER_NAME = "daily_occupation"
DAILY_OCCUPATION_PARAMETER_DESCRIPTION = "The description of the current daily occupation of the character, written in natural English."

CHARACTER_RECENT_PROGRESS_IN_LIFE_GPT_SYSTEM_CONTENT = "I am CharacterRecentProgressInLifeDeterminerGPT. I have the responsibility of describing the feeling "
CHARACTER_RECENT_PROGRESS_IN_LIFE_GPT_SYSTEM_CONTENT += " about his or her recent progress in life given a list of that character's memories."
GET_CHARACTER_RECENT_PROGRESS_IN_LIFE_FUNCTION_NAME = (
    "get_character_recent_progress_in_life"
)
GET_CHARACTER_RECENT_PROGRESS_IN_LIFE_FUNCTION_DESCRIPTION = "Gets a character's feeling about his or her recent progress in life from a list of "
GET_CHARACTER_RECENT_PROGRESS_IN_LIFE_FUNCTION_DESCRIPTION += (
    "memories belonging to that character."
)
RECENT_PROGRESS_IN_LIFE_PARAMETER_NAME = "recent_progress_in_life"
RECENT_PROGRESS_IN_LIFE_PARAMETER_DESCRIPTION = "The description of the character's feeling about his or her recent progress in life, written in natural English."

CHARACTER_TRAITS_GPT_SYSTEM_CONTENT = "I am CharacterTraitsDeterminerGPT. I have the responsibility of creating a list of adjectives, separated with commas, "
CHARACTER_TRAITS_GPT_SYSTEM_CONTENT += "that describe the traits of a character."
GET_CHARACTER_TRAITS_FUNCTION_NAME = "get_character_traits"
GET_CHARACTER_TRAITS_FUNCTION_DESCRIPTION = "Gets a character's traits as a list of comma-separated adjectives, from a list of memories belonging to that character."
TRAITS_PARAMETER_NAME = "traits"
TRAITS_PARAMETER_DESCRIPTION = (
    "A comma-separated list of adjectives that describe the character's traits."
)


class CharacterSummaryCreator:
    """This class handles creating and saving to file the character summary for any given character."""

    def __init__(self, agent_name: str, current_timestamp: datetime):
        """Creates an instance of the class CharacterSummaryCreator

        Args:
            agent_name (str): the name of the agent whose character summary will be created.
            current_timestamp (datetime): the current timestamp.

        Raises:
            FileNotFoundError: if the memories database doesn't exist for the given character.
        """
        # First ensure that a memories database exists for this agent.
        if not os.path.isfile(get_base_memories_full_path(agent_name)):
            error_message = f"The class {CharacterSummaryCreator.__name__} failed to find a memories database at {get_base_memories_full_path(agent_name)}"
            raise FileNotFoundError(error_message)

        self._agent_name = agent_name
        self._current_timestamp = current_timestamp

    def _determine_character_attribute(
        self, determine_character_attribute_parameters: dict
    ):
        """Relies on the AI model to determine a character attribute.

        Args:
            determine_character_attribute_parameters (dict): contains all the necessary arguments for this function.
                The keys for this dict are the following:
                'memories_database_querier'
                'query'
                'system_content'
                'function_name'
                'function_description'
                'parameter_name'
                'parameter_type'
                'parameter_description'
                'model'

        Returns:
            str or int: the character's attribute determined by the AI.
        """
        query_results = determine_character_attribute_parameters[
            "memories_database_querier"
        ].query(determine_character_attribute_parameters["query"], 30)

        messages = []
        messages.append(
            {
                "role": SYSTEM_ROLE,
                "content": determine_character_attribute_parameters["system_content"],
            }
        )

        user_content = f"Determine {determine_character_attribute_parameters['parameter_description']} of {self._agent_name} "
        user_content += (
            "given the following list of memories of that character:\n"
            + " ".join(query_results)
        )
        messages.append(
            {
                "role": USER_ROLE,
                "content": user_content,
            }
        )

        functions = []
        functions.append(
            {
                "name": determine_character_attribute_parameters["function_name"],
                "description": determine_character_attribute_parameters[
                    "function_description"
                ],
                "parameters": {
                    "type": "object",
                    "properties": {
                        determine_character_attribute_parameters["parameter_name"]: {
                            "type": determine_character_attribute_parameters[
                                "parameter_type"
                            ],
                            "description": determine_character_attribute_parameters[
                                "parameter_description"
                            ],
                        }
                    },
                    "required": [
                        determine_character_attribute_parameters["parameter_name"]
                    ],
                },
            }
        )

        response = request_ai_response_with_functions(
            messages,
            functions,
            function_call={
                "name": determine_character_attribute_parameters["function_name"]
            },
            model=determine_character_attribute_parameters["model"],
        )

        function_arguments = load_arguments_of_message_with_function_call(
            get_message_from_gpt_response(response)
        )

        return function_arguments.get(
            determine_character_attribute_parameters["parameter_name"]
        )

    def _determine_character_traits(
        self, memories_database_querier: MemoriesDatabaseQuerier
    ):
        """Relies on the AI model to determine the character's traits.

        Args:
            memories_database_querier (MemoriesDatabaseQuerier): an instance of the class that handles queries to the memories database.

        Returns:
            str: the character's traits, as a list of adjectives.
        """
        return self._determine_character_attribute(
            {
                "memories_database_querier": memories_database_querier,
                "query": f"{self._agent_name}'s traits.",
                "system_content": CHARACTER_TRAITS_GPT_SYSTEM_CONTENT,
                "function_name": GET_CHARACTER_TRAITS_FUNCTION_NAME,
                "function_description": GET_CHARACTER_TRAITS_FUNCTION_DESCRIPTION,
                "parameter_name": TRAITS_PARAMETER_NAME,
                "parameter_type": "string",
                "parameter_description": TRAITS_PARAMETER_DESCRIPTION,
                "model": GPT_3_5,
            }
        )

    def _determine_recent_progress_in_life(
        self, memories_database_querier: MemoriesDatabaseQuerier
    ):
        """Relies on the AI model to determine the character's recent progress in life.

        Args:
            memories_database_querier (MemoriesDatabaseQuerier): an instance of the class that handles queries to the memories database.

        Returns:
            str: the character's recent progress in life.
        """
        return self._determine_character_attribute(
            {
                "memories_database_querier": memories_database_querier,
                "query": f"{self._agent_name}'s feeling about his or her recent progress in life.",
                "system_content": CHARACTER_RECENT_PROGRESS_IN_LIFE_GPT_SYSTEM_CONTENT,
                "function_name": GET_CHARACTER_RECENT_PROGRESS_IN_LIFE_FUNCTION_NAME,
                "function_description": GET_CHARACTER_RECENT_PROGRESS_IN_LIFE_FUNCTION_DESCRIPTION,
                "parameter_name": RECENT_PROGRESS_IN_LIFE_PARAMETER_NAME,
                "parameter_type": "string",
                "parameter_description": RECENT_PROGRESS_IN_LIFE_PARAMETER_DESCRIPTION,
                "model": GPT_4,
            }
        )

    def _determine_current_daily_occupation(
        self, memories_database_querier: MemoriesDatabaseQuerier
    ):
        """Relies on the AI model to determine the character's daily occupation.

        Args:
            memories_database_querier (MemoriesDatabaseQuerier): an instance of the class that handles queries to the memories database.

        Returns:
            str: the character's current daily occupation.
        """
        return self._determine_character_attribute(
            {
                "memories_database_querier": memories_database_querier,
                "query": f"{self._agent_name}'s current daily occupation.",
                "system_content": CHARACTER_DAILY_OCCUPATION_GPT_SYSTEM_CONTENT,
                "function_name": GET_CHARACTER_DAILY_OCCUPATION_FUNCTION_NAME,
                "function_description": GET_CHARACTER_DAILY_OCCUPATION_FUNCTION_DESCRIPTION,
                "parameter_name": DAILY_OCCUPATION_PARAMETER_NAME,
                "parameter_type": "string",
                "parameter_description": DAILY_OCCUPATION_PARAMETER_DESCRIPTION,
                "model": GPT_4,
            }
        )

    def _determine_character_age(
        self, memories_database_querier: MemoriesDatabaseQuerier
    ):
        """Relies on the AI model to determine the character's age

        Args:
            memories_database_querier (MemoriesDatabaseQuerier): an instance of the class that handles queries to the memories database.

        Returns:
            int: the character's age.
        """
        # Determine the character's age
        return self._determine_character_attribute(
            {
                "memories_database_querier": memories_database_querier,
                "query": f"{self._agent_name}'s current age.",
                "system_content": CHARACTER_AGE_DETERMINER_GPT_SYSTEM_CONTENT,
                "function_name": GET_CHARACTER_AGE_FUNCTION_NAME,
                "function_description": GET_CHARACTER_AGE_FUNCTION_DESCRIPTION,
                "parameter_name": AGE_PARAMETER_NAME,
                "parameter_type": "integer",
                "parameter_description": AGE_PARAMETER_DESCRIPTION,
                "model": GPT_3_5,
            }
        )

    def _determine_character_core_characteristics(
        self, memories_database_querier: MemoriesDatabaseQuerier
    ):
        """Relies on the AI model to determine the character's core characteristics.

        Args:
            memories_database_querier (MemoriesDatabaseQuerier): an instance of the class that handles queries to the memories database.

        Returns:
            str: the character's core characteristics.
        """
        return self._determine_character_attribute(
            {
                "memories_database_querier": memories_database_querier,
                "query": f"{self._agent_name}'s core characteristics.",
                "system_content": CHARACTER_CORE_CHARACTERISTICS_GPT_SYSTEM_CONTENT,
                "function_name": GET_CHARACTER_CORE_CHARACTERISTICS_FUNCTION_NAME,
                "function_description": GET_CHARACTER_CORE_CHARACTERISTICS_FUNCTION_DESCRIPTION,
                "parameter_name": CORE_CHARACTERISTICS_PARAMETER_NAME,
                "parameter_type": "string",
                "parameter_description": CORE_CHARACTERISTICS_PARAMETER_DESCRIPTION,
                "model": GPT_4,
            }
        )

    def create(self):
        """Creates and saves to file the character summary of the passed character."""
        # If a character summary already exists, this operation is going to overwrite it.

        index, raw_memories = MemoriesDatabaseLoader(self._agent_name).load()

        memories_database_querier = MemoriesDatabaseQuerier(
            self._agent_name, self._current_timestamp, raw_memories, index
        )

        # Determine the character's age.
        age = self._determine_character_age(memories_database_querier)

        # Determine the character's traits.
        traits = self._determine_character_traits(memories_database_querier)

        # Determine the character's core characteristics.
        core_characteristics = self._determine_character_core_characteristics(
            memories_database_querier
        )

        # Determine the character's current daily occupation.
        daily_occupation = self._determine_current_daily_occupation(
            memories_database_querier
        )

        # Determine the character's feeling for his or her current progress in life.
        recent_progress_in_life = self._determine_recent_progress_in_life(
            memories_database_querier
        )

        # Make sure to unload the database.
        index.unload()

        # Save the character summary to a file.
        with open(
            get_character_summary_full_path(self._agent_name), "w", encoding="utf-8"
        ) as file:
            file.write(
                f"Name: {self._agent_name} (age {age})\nTraits: {traits}\n{core_characteristics}\n{daily_occupation}\n{recent_progress_in_life}"
            )
