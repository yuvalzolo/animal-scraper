from typing import List

class Animal:
    # Represents an animal with its name and list of collateral adjectives
    def __init__(self, name: str, adjectives: List[str]):
        self.name = name
        self.adjectives = adjectives
