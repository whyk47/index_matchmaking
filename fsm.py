import re

from transitions import Machine


class SwapExtractor:
    # Define the states
    states = ("idle", "module_identified", "in_have_section", "in_want_section")

    def __init__(self):
        self.offers = []
        self.current_offer = None

        # Initialize the FSM
        self.machine = Machine(model=self, states=SwapExtractor.states, initial="idle")

        # Define Transitions
        # 1. When a module is found, start a new offer and reset state
        self.machine.add_transition(
            "found_module", "*", "module_identified", after="start_new_offer"
        )
        # 2. Transition to HAVE section
        self.machine.add_transition(
            "found_have", ["module_identified", "in_want_section"], "in_have_section"
        )
        # 3. Transition to WANT section
        self.machine.add_transition(
            "found_want", ["module_identified", "in_have_section"], "in_want_section"
        )
        # 4. Return to idle after finishing a block
        self.machine.add_transition("reset", "*", "idle")

        # Patterns
        self.re_module = r"([A-Z]{2}\d{4})"
        self.re_index = r"\b(\d{5})\b"
        # Captures days and timeslots (e.g., Mon 1030-1220) [cite: 1, 3]
        self.re_time = r"((?:Mon|Tue|Wed|Thu|Fri|Monday|Tuesday|Wednesday|Thursday|Friday)\b.*?\d{2,4}[-\s:]{1,3}(?:to\s)?\d{2,4})"

    def start_new_offer(self, module_code):
        if self.current_offer:
            self.offers.append(self.current_offer)
        self.current_offer = {
            "module": module_code.upper(),
            "have_index": None,
            "have_timeslot": None,
            "want_indexes": [],
            "want_timeslots": [],
        }

    def parse(self, text):
        lines = text.split("\n")
        for line in lines:
            words = line.split()
            for word in words:
                print(self.state, word)
                word = word.strip()
                if not word:
                    continue
                if word == "```":
                    self.reset()
                    continue

                # Event: Module Code Found [cite: 1, 3]
                module_match = re.search(self.re_module, word, re.IGNORECASE)
                if module_match:
                    print(self.current_offer)
                    self.start_new_offer(module_match.group(1))
                    self.found_module(module_match.group(1))

                # Event: Section Keywords Found
                if "have" in word.lower() and self.state != "idle":
                    self.found_have()
                elif "want" in word.lower() and self.state != "idle":
                    self.found_want()
                # Data Extraction logic based on state
                if self.state == "in_have_section":
                    idx = re.search(self.re_index, word)  # [cite: 1]
                    tm = re.search(self.re_time, word, re.IGNORECASE)  # [cite: 1, 2]
                    if idx:
                        self.current_offer["have_index"] = idx.group(1)
                    if tm:
                        self.current_offer["have_timeslot"] = tm.group(1)

                elif self.state == "in_want_section":
                    indices = re.findall(self.re_index, word)  # [cite: 1, 3]
                    times = re.findall(
                        self.re_time, word, re.IGNORECASE
                    )  # [cite: 1, 3]
                    if indices:
                        self.current_offer["want_indexes"].extend(indices)
                    if times:
                        self.current_offer["want_timeslots"].extend(
                            [t.strip() for t in times]
                        )

        # Save the last one
        if self.current_offer:
            print(self.current_offer)
            self.offers.append(self.current_offer)
        return self.offers


# Usage
extractor = SwapExtractor()
with open("messages.txt", "r", encoding="utf-8") as f:
    full_content = f.read()
results = extractor.parse(full_content)  # Process the messages.txt content
