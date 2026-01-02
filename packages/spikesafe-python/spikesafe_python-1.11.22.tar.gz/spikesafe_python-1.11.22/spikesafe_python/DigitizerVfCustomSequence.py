from __future__ import annotations
from .DigitizerVfCustomSequenceStep import DigitizerVfCustomSequenceStep

class DigitizerVfCustomSequence:
    """
    Represents a custom sequence for the Digitizer.

    Attributes
    ----------
    sequence_steps : list[DigitizerVfCustomSequenceStep]
        A list of DigitizerVfCustomSequenceStep objects that represent the steps in the custom sequence

    Methods
    -------
    parse_sequence(sequence: str) -> DigitizerVfCustomSequence
        Parses a custom sequence string into a DigitizerVfCustomSequence object
    get_aperture_for_sample_number_in_seconds(sample_number: int) -> float
        Returns the aperture in seconds for a given sample number
    is_first_sample_in_step(sample_number: int) -> bool
        Returns True if the sample number is the first sample in a step, otherwise False
    get_total_number_of_samples() -> int
        Returns the total number of samples in the sequence
    get_total_time_seconds() -> float
        Returns the total time in seconds for the sequence
    """
    def __init__(self) -> None:
        self.sequence_steps: list[DigitizerVfCustomSequenceStep] = []

    def parse_sequence(self, sequence: str) -> DigitizerVfCustomSequence:
        """
        Parses a custom sequence string into a DigitizerVfCustomSequence object
        """
        self.sequence_steps.clear()
        step_strings = sequence.split(',')

        for step_string in step_strings:
            parts = step_string.split('@')
            if len(parts) == 2:
                try:
                    number_of_samples = int(parts[0])
                    aperture_in_microseconds = int(parts[1])

                    self.sequence_steps.append(DigitizerVfCustomSequenceStep(
                        step_number=len(self.sequence_steps) + 1,
                        number_of_samples=number_of_samples,
                        aperture_in_microseconds=aperture_in_microseconds
                    ))
                except ValueError:
                    continue
        
        return self

    def get_aperture_for_sample_number_in_seconds(self, sample_number: int) -> float:
        """
        Returns the aperture in seconds for a given sample number
        """
        current_sample_count = 0

        for step in self.sequence_steps:
            for i in range(step.number_of_samples):
                current_sample_count += 1
                if current_sample_count == sample_number:
                    return step.aperture_in_microseconds / 1_000_000.0

        raise IndexError("Sample number exceeds the total number of samples in the sequence.")

    def is_first_sample_in_step(self, sample_number: int) -> bool:
        """
        Returns True if the sample number is the first sample in a step, otherwise False
        """
        current_sample_count = 0

        for step in self.sequence_steps:
            first_sample_in_step = current_sample_count + 1

            if sample_number == first_sample_in_step:
                return True

            current_sample_count += step.number_of_samples

        return False

    def get_total_number_of_samples(self) -> int:
        """
        Returns the total number of samples in the sequence
        """
        total_samples = sum(step.number_of_samples for step in self.sequence_steps)
        return total_samples

    def get_total_time_seconds(self) -> float:
        """
        Returns the total time in seconds for the sequence
        """
        total_time = sum(step.number_of_samples * step.aperture_in_microseconds for step in self.sequence_steps)
        return total_time / 1000000
