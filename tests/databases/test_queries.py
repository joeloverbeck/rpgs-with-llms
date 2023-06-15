import unittest
from databases.creation import create_vector_database_for_agent

from enums.enums import VectorDatabaseType
from files.existence import file_exists
from paths.full_paths import get_base_character_attributes_full_path


class TestProcessObservation(unittest.TestCase):
    def setUp(self):
        agent_name = "test"

        if not file_exists(get_base_character_attributes_full_path(agent_name)):
            # create the corresponding vector database
            create_vector_database_for_agent(
                agent_name, VectorDatabaseType.CHARACTER_ATTRIBUTES
            )

    def test_can_query_test_character_attributes(self):
        # this test assumes that the 'ann' file has already been created
        agent_name = "test"

        self.assertTrue(
            file_exists(get_base_character_attributes_full_path(agent_name))
        )


if __name__ == "__main__":
    unittest.main()
