
import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):
        self.height = height
        self.width = width
        self.mines = set()

        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        self.mines_found = set()

    def print(self):
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        count = 0

        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if (i, j) == cell:
                    continue

                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        return self.mines_found == self.mines


class Sentence():
    """
    A logical sentence containing cells and a mine count.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        if self.count == len(self.cells):
            return self.cells.copy()
        return set()

    def known_safes(self):
        if self.count == 0:
            return self.cells.copy()
        return set()

    def mark_mine(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper AI player using logical inference.
    """

    def __init__(self, height=8, width=8):
        self.height = height
        self.width = width

        self.moves_made = set()
        self.mines = set()
        self.safes = set()
        self.knowledge = []

    def mark_mine(self, cell):
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Add information from a revealed safe cell.
        Infer mines, safe cells, and new sentences.
        """

        # Record the cell as played and safe.
        self.moves_made.add(cell)
        self.mark_safe(cell)

        # Build a sentence using unknown neighbors.
        neighbors = set()
        remaining_count = count
        row, col = cell

        for i in range(max(0, row - 1), min(self.height, row + 2)):
            for j in range(max(0, col - 1), min(self.width, col + 2)):
                neighbor = (i, j)

                if neighbor == cell:
                    continue

                if neighbor in self.mines:
                    remaining_count -= 1

                elif neighbor not in self.safes:
                    neighbors.add(neighbor)

        # Add the new knowledge sentence.
        if neighbors:
            sentence = Sentence(neighbors, remaining_count)

            if sentence not in self.knowledge:
                self.knowledge.append(sentence)

        # Repeat deductions until no new facts are found.
        while True:
            changed = False
            new_mines = set()
            new_safes = set()

            # Find mines and safe cells implied by sentences.
            for sentence in self.knowledge:
                new_mines.update(sentence.known_mines())
                new_safes.update(sentence.known_safes())

            # Mark newly discovered mines.
            for mine in new_mines - self.mines:
                self.mark_mine(mine)
                changed = True

            # Mark newly discovered safe cells.
            for safe in new_safes - self.safes:
                self.mark_safe(safe)
                changed = True

            # Remove empty sentences.
            remaining = [
                sentence
                for sentence in self.knowledge
                if sentence.cells
            ]

            if len(remaining) != len(self.knowledge):
                self.knowledge = remaining
                changed = True

            # Infer new sentences using subset relationships.
            inferred = []

            for first in self.knowledge:
                for second in self.knowledge:

                    if first.cells < second.cells:
                        cells = second.cells - first.cells
                        mines = second.count - first.count

                        if 0 <= mines <= len(cells):
                            candidate = Sentence(cells, mines)

                            if (
                                candidate not in self.knowledge
                                and candidate not in inferred
                            ):
                                inferred.append(candidate)

            if inferred:
                self.knowledge.extend(inferred)
                changed = True

            if not changed:
                break

    def make_safe_move(self):
        """
        Return a known safe cell that has not been played.
        """

        available = self.safes - self.moves_made

        if available:
            return sorted(available)[0]

        return None

    def make_random_move(self):
        """
        Return a random cell that has not been played
        and is not known to contain a mine.
        """

        available = [
            (i, j)
            for i in range(self.height)
            for j in range(self.width)
            if (i, j) not in self.moves_made
            and (i, j) not in self.mines
        ]

        if available:
            return random.choice(available)

        return None
