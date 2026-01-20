import enum


class DifficultyLevel(enum.StrEnum):
    EASY = "easy"
    MODERATE = "moderate"
    HARD = "hard"
    EXPERT = "expert"
    IMPOSSIBLE = "impossible"

    @enum.nonmember
    class Labels:
        EASY = "Easy Peasy"
        MODERATE = "Moderate Challenge"
        HARD = "Advanced Pet Wrangling"
        EXPERT = "Call in the Professionals"
        IMPOSSIBLE = "May God Have Mercy on My Soul"
