from barcode_validator.config import Config
from nbt import Taxon
from typing import List, Optional
import logging


def result_fields():
    """
    Returns a tab-separated string containing the result fields.
    :return:
    """
    return "Process ID\tSequence Length\tObserved Taxon\tExpected Taxon\tSpecies\tStop Codons\tAmbiguities\tPasses " \
           "All Checks"


class DNAAnalysisResult:
    def __init__(self, process_id):
        self.process_id: str = process_id
        self._seq_length: Optional[int] = None
        self._obs_taxon: List[Taxon] = []
        self._exp_taxon: Optional[Taxon] = None
        self._species: Optional[Taxon] = None
        self._stop_codons = []
        self._ambiguities = None

    @property
    def seq_length(self) -> Optional[int]:
        """
        Getter for the sequence length.
        :return: an integer representing the sequence length
        """
        return self._seq_length

    @seq_length.setter
    def seq_length(self, value: int) -> None:
        """
        Setter for the sequence length.
        :param value: an integer representing the sequence length
        :return:
        """
        if not isinstance(value, int) or value <= 0:
            raise ValueError("seq_length must be a positive integer")
        self._seq_length = value

    @property
    def obs_taxon(self) -> List[Taxon]:
        """
        Getter for the observed taxon.
        :return: A list of strings representing the observed taxon
        """
        return self._obs_taxon

    @obs_taxon.setter
    def obs_taxon(self, taxa: List[Taxon]) -> None:
        """
        Setter for the observed taxon.
        :param taxa: A list of strings representing the observed taxon
        :return:
        """
        if not isinstance(taxa, list) or not all(isinstance(item, Taxon) for item in taxa):
            logging.error(taxa)
            raise ValueError("obs_taxon must be a list of Taxon objects")
        self._obs_taxon = taxa

    def add_obs_taxon(self, taxon: Taxon) -> None:
        """
        Add an observed taxon to the list.
        :param taxon: A string representing the observed taxon
        :return:
        """
        if not isinstance(taxon, Taxon):
            raise ValueError("Taxon must be a Taxon object")
        if taxon not in self._obs_taxon:
            self._obs_taxon.append(taxon)

    @property
    def exp_taxon(self) -> Optional[Taxon]:
        """
        Getter for the expected taxon.
        :return: A Taxon object representing the expected taxon
        """
        return self._exp_taxon

    @exp_taxon.setter
    def exp_taxon(self, taxon: Taxon) -> None:
        """
        Setter for the expected taxon.
        :param taxon: A Taxon object representing the expected taxon
        :return:
        """
        if not isinstance(taxon, Taxon):
            raise ValueError("exp_taxon must be a Taxon object")
        self._exp_taxon = taxon

    @property
    def species(self) -> Optional[Taxon]:
        """
        Getter for the species name.
        :return: A Taxon object representing the species name
        """
        return self._species

    @species.setter
    def species(self, species: Taxon) -> None:
        """
        Setter for the species name.
        :param species: A Taxon object representing the species name
        :return:
        """
        if not isinstance(species, Taxon):
            raise ValueError("species must be a Taxon object")
        self._species = species

    @property
    def stop_codons(self) -> List[int]:
        """
        Getter for the stop codons.
        :return: A list of integers representing the stop codon positions
        """
        return self._stop_codons

    @stop_codons.setter
    def stop_codons(self, codon_positions: List[int]) -> None:
        """
        Setter for the stop codons.
        :param codon_positions: A list of integers representing the stop codon positions
        :return:
        """
        if not isinstance(codon_positions, list) or not all(isinstance(x, int) and x >= 0 for x in codon_positions):
            raise ValueError("stop_codons must be a list of non-negative integers")
        self._stop_codons = codon_positions

    @property
    def ambiguities(self) -> Optional[int]:
        """
        Getter for the number of ambiguities.
        :return: An integer representing the number of ambiguities
        """
        return self._ambiguities

    @ambiguities.setter
    def ambiguities(self, n_ambiguities: int) -> None:
        """
        Setter for the number of ambiguities.
        :param n_ambiguities: An integer representing the number of ambiguities
        :return:
        """
        if not isinstance(n_ambiguities, int) or n_ambiguities < 0:
            raise ValueError("ambiguities must be a non-negative integer")
        self._ambiguities = n_ambiguities

    def add_stop_codon(self, position: int) -> None:
        """
        Add a stop codon position to the list.
        :param position: An integer representing the stop codon position
        :return:
        """
        if not isinstance(position, int) or position < 0:
            raise ValueError("Stop codon position must be a non-negative integer")
        self._stop_codons.append(position)

    def check_length(self) -> bool:
        """
        Check if the sequence length meets the minimum requirement.
        :return: A boolean indicating whether the sequence length is valid
        """
        config = Config()
        min_length = config.get('min_seq_length')
        return self.seq_length >= min_length if self.seq_length is not None else False

    def check_taxonomy(self) -> bool:
        """
        Check if expected taxon is in the observed taxon list.
        :return: A boolean indicating whether the taxonomy check passed
        """
        return self.exp_taxon in [taxon for taxon in self.obs_taxon] if self.obs_taxon and self.exp_taxon else False

    def check_pseudogene(self) -> bool:
        """
        Check if the sequence contains stop codons, i.e. if the list of stop codon locations is empty.
        :return: A boolean indicating whether the sequence is a pseudogene
        """
        return len(self.stop_codons) == 0

    def passes_all_checks(self) -> bool:
        """
        Check if the sequence passes all quality checks.
        :return: A boolean indicating whether the sequence passes all checks
        """
        return self.check_length() and self.check_taxonomy() and self.check_pseudogene()

    def __str__(self) -> str:
        """
        String representation of the result object.
        :return: A tab-separated string containing the result fields
        """
        results = [
            self.process_id,
            self.seq_length,
            ', '.join(str(taxon) for taxon in self.obs_taxon),  # Convert each Taxon to string
            str(self.exp_taxon),  # Convert Taxon to string
            str(self.species),  # Convert Taxon to string
            self.stop_codons,
            self.ambiguities,
            self.passes_all_checks()
        ]
        return '\t'.join(map(str, results))

