from annoy import AnnoyIndex

from defines.defines import DECAY_RATE, MODEL, NUMBER_OF_BASE_RESULTS_FOR_EVERY_QUERY
from math_utils import calculate_recency, calculate_score
from memories.jsonification import format_python_memory_data_for_json
from memories.saving import save_memories_to_json_file_ensuring_parity
from paths.full_paths import get_base_memories_json_full_path


class MemoriesDatabaseQuerier:
    def __init__(
        self, agent_name, current_timestamp, memories_raw_data: dict, index: AnnoyIndex
    ):
        self._agent_name = agent_name
        self._current_timestamp = current_timestamp
        self._memories_raw_data = memories_raw_data
        self._index = index

    def query(self, query: str, number_of_results: int) -> list[str]:
        """Queries the memories database for the passed query.
        Note: this function doesn't close the index detabase.

        Args:
            query (str): the text with which the database will be queried.
            number_of_results (int): how many relevant results will be return.
        """
        # Get nearest neighbors from the Annoy index
        nearest_neighbors = self._index.get_nns_by_vector(
            MODEL.encode(query),
            NUMBER_OF_BASE_RESULTS_FOR_EVERY_QUERY,
            include_distances=True,
        )

        # Calculate the custom scores
        scores = self._calculate_custom_scores_of_memories(nearest_neighbors)

        # Sort the results by the custom scores in descending order
        scores = sorted(scores, key=lambda x: x[1], reverse=True)

        self._update_most_recent_access_timestamps(scores, number_of_results)

        return [
            f"{self._memories_raw_data[str(entry[0])]['description']}"
            for entry in scores[:number_of_results]
        ]

    def _calculate_custom_scores_of_memories(self, nearest_neighbors):
        scores = []

        for idx, distance in zip(nearest_neighbors[0], nearest_neighbors[1]):
            relevance = 1 - distance
            recency = self._memories_raw_data[str(idx)]["recency"]
            importance = self._memories_raw_data[str(idx)]["importance"]
            score = calculate_score(relevance, recency, importance)
            scores.append((idx, score))

        return scores

    def _update_most_recent_access_timestamps(self, scores, number_of_results):
        """Updates the most recent access timestamps of query results.

        Args:
            scores (list): a scored and ordered list of relevant results of the query.

        Returns:
            dict: the memories in raw data format, with updated 'most_recent_access_timestamp' and 'recency' values
        """

        base_memories_json_full_path = get_base_memories_json_full_path(
            self._agent_name
        )

        # Update the 'most_recent_access_timestamp' as well as the 'recency' values of each entry
        for idx, _ in scores[:number_of_results]:
            # locate in memories_raw_data which are those records

            self._memories_raw_data[str(idx)]["recency"] = calculate_recency(
                self._current_timestamp, self._current_timestamp, DECAY_RATE
            )

            self._memories_raw_data[str(idx)][
                "most_recent_access_timestamp"
            ] = self._current_timestamp.isoformat()

        # After we have modified the most 'recent_access_timestamp' values, we have to ensure
        # that we format the memories_raw_data into jsonificable values (meaning that we turn the dates into text.)
        self._memories_raw_data = format_python_memory_data_for_json(
            self._memories_raw_data
        )

        save_memories_to_json_file_ensuring_parity(
            base_memories_json_full_path, self._memories_raw_data, self._index
        )
