"""This module contains the DatabaseQuerier, that handles queries to a vector database.
"""
from datetime import datetime
from typing import List, Tuple
from annoy import AnnoyIndex

from defines.defines import MODEL, NUMBER_OF_BASE_RESULTS_FOR_EVERY_QUERY
from math_utils import calculate_score
from vector_databases.database_entry import DatabaseEntry
from vector_databases.database_updater import DatabaseUpdater


class DatabaseQuerier:
    """This class handles queries to a vector database."""

    def __init__(
        self,
        current_timestamp: datetime,
        raw_data: dict,
        index: AnnoyIndex,
        database_full_path: str,
        database_json_full_path: str,
        database_updater: DatabaseUpdater,
    ):
        """Initializes an instance of the DatabaseQuerier class.

        Args:
            current_timestamp (datetime): the current timestamp.
            raw_data (dict): the raw data of the vector database (the content of the json file).
            index (AnnoyIndex): the index of the vector database.
            database_full_path (str): the full path to the 'ann' file of the vector database.
            database_json_full_path (str): the full path to the 'json' file of the vector database.
            database_updater (DatabaseUpdater): the class responsible for updating the vector database.
        """
        self._current_timestamp = current_timestamp
        self._raw_data = raw_data
        self._index = index
        self._database_full_path = database_full_path
        self._database_json_full_path = database_json_full_path
        self._database_updater = database_updater

    def query(self, query: str, number_of_results: int) -> List[str]:
        """Queries the vector database for the passed query.
        It also updates the recent access timestamps for the returned results.
        Note: this function doesn't close the corresponding AnnoyIndex.


        Args:
            query (str): the text with which the database will be queried.
            number_of_results (int): how many relevant results will be return.
        """
        if not isinstance(query, str):
            raise TypeError(
                f"The function {self.query.__name__} expected 'query' to be a string. It was: {query}"
            )
        if not isinstance(number_of_results, int):
            raise TypeError(
                f"The function {self.query.__name__} expected 'number_of_results' to be an int. It was: {number_of_results}"
            )
        if not number_of_results > 0:
            raise ValueError(
                f"The function {self.query.__name__} expected 'number_of_results' to be greater than zero, but it was: {number_of_results}"
            )

        # Get nearest neighbors from the Annoy index
        nearest_neighbors = self._index.get_nns_by_vector(
            MODEL.encode(query),
            NUMBER_OF_BASE_RESULTS_FOR_EVERY_QUERY,
            include_distances=True,
        )

        # Calculate the custom scores
        scores = self._calculate_custom_scores_of_query_results(nearest_neighbors)

        # Sort the results by the custom scores in descending order
        scores = sorted(scores, key=lambda x: x[1], reverse=True)

        # limit the scores to those we are going to return
        scores = scores[:number_of_results]

        # Now that we have determined a subset of scores to return (those ordered
        # by descending order of scores, we must update their most recent access timestamps.)
        self._database_updater.update_most_recent_access_timestamps(
            scores, self._index, self._raw_data
        )

        return [f"{entry[0].get_description()}" for entry in scores]

    def _calculate_custom_scores_of_query_results(
        self, nearest_neighbors: List[int]
    ) -> List[Tuple[DatabaseEntry, float]]:
        """Calculates the custom scores of a list of data returned from the vector database.

        Returns:
            List[Tuple[DatabaseEntry, float]]: a list containing tuples of DatabaseEntry along with its score.
        """
        scores = []

        for idx, distance in zip(nearest_neighbors[0], nearest_neighbors[1]):
            database_entry = DatabaseEntry(idx, self._raw_data[str(idx)])

            relevance = 1 - distance
            recency = database_entry.get_recency()
            importance = database_entry.get_importance()
            score = calculate_score(relevance, recency, importance)
            scores.append((database_entry, score))

        return scores
