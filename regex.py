from __future__ import annotations
from abc import ABC, abstractmethod


class State(ABC):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """
        function checks whether occured character is handled by current ctate
        """
        pass

    def check_next(self, next_char: str) -> State | Exception:
        for state in self.next_states:
            if state.check_self(next_char):
                return state
        raise NotImplementedError("rejected string")


class StartState(State):
    '''
    beggining state
    '''
    next_states: list[State] = []

    def __init__(self):
        '''
        initalizes attributes
        '''
        super().__init__()

    def check_self(self, char):
        '''
        checks whether can have char in this state
        '''
        return super().check_self(char)


class TerminationState(State):
    '''
    final state
    '''
    def __init__(self):
        '''
        initalizes attributes
        '''
        super().__init__()
    def check_self(self, char):
        '''
        checks whether can have char in this state
        '''
        return True


class DotState(State):
    """
    state for . character (any character accepted)
    """

    next_states: list[State] = []

    def __init__(self):
        '''
        initalizes attributes
        '''
        super().__init__()

    def check_self(self, char: str):
        '''
        checks whether can have char in this state
        '''
        return True


class AsciiState(State):
    """
    state for alphabet letters or numbers
    """

    next_states: list[State] = []

    def __init__(self, symbol: str) -> None:
        '''
        initalizes attributes
        '''

        self.curr_sym = symbol

    def check_self(self, curr_char: str) -> State | Exception:
        '''
        checks whether can have char in this state
        '''
        return curr_char == self.curr_sym


class StarState(State):
    '''
    state for repeating character zero or more times
    '''
    next_states: list[State] = []

    def __init__(self, checking_state: State):
        '''
        initalizes attributes
        '''
        self.checking_state = checking_state

    def check_self(self, char):
        '''
        checks whether can have char in this state
        '''
        return self.checking_state.check_self(char)


class PlusState(State):
    '''
    state for repeating character once or more
    '''
    next_states: list[State] = []

    def __init__(self, checking_state: State):
        '''
        initalizes attributes
        '''
        self.checking_state = checking_state

    def check_self(self, char):
        '''
        checks whether can have char in this state
        '''
        return self.checking_state.check_self(char)


class RegexFSM:
    '''
    class for creating state sequence for regex and checking string
    '''
    curr_state: State = StartState()

    def __init__(self, regex_expr: str) -> None:
        '''
        initializes states for regex_expr
        '''
        super_prev = None
        prev_state = self.curr_state
        tmp_next_state = self.curr_state

        for char in regex_expr:
            if char == '+':
                tmp_next_state = self.__init_next_state(char, prev_state, tmp_next_state)
                prev_state.next_states.append(tmp_next_state)
                super_prev = prev_state
                prev_state = tmp_next_state

            elif char == '*':
                tmp_next_state = self.__init_next_state(char, prev_state, tmp_next_state)
                prev_state.next_states.append(tmp_next_state)


            else:
                tmp_next_state = self.__init_next_state(char, prev_state, tmp_next_state)

                prev_state.next_states.append(tmp_next_state)
                if super_prev is not None:
                    super_prev.next_states.append(tmp_next_state)
                super_prev = prev_state
                prev_state = tmp_next_state

        termination = TerminationState()
        tmp_next_state.next_states.append(termination)

    def __init_next_state(
        self, next_token: str, prev_state: State, tmp_next_state: State
    ) -> State:
        '''
        finds next states
        '''
        new_state = None

        match next_token:
            case next_token if next_token == ".":
                new_state = DotState()
            case next_token if next_token == "*":
                new_state = StarState(tmp_next_state)

                tmp_next_state.next_states.append(tmp_next_state)

            case next_token if next_token == "+":
                new_state = PlusState(tmp_next_state)
                tmp_next_state.next_states.append(tmp_next_state)

            case next_token if next_token.isascii():
                new_state = AsciiState(next_token)

            case _:
                raise AttributeError("Character is not supported")


        return new_state

    def check_string(self, string):
        '''
        checks string
        '''
        our_state = self.curr_state
        possible_next_states = [our_state]
        for char in string:
            new_possible_next_states = []

            for state in possible_next_states:
                if isinstance(state, TerminationState):
                    break
                for s_state in state.next_states:
                    if s_state.check_self(char):
                        if s_state not in new_possible_next_states:
                            new_possible_next_states.append(s_state)
            possible_next_states = new_possible_next_states


        for other_state in possible_next_states:
            if isinstance(other_state, TerminationState):
                return True
        return False



if __name__ == "__main__":
    regex_pattern = "a*4.+hi"

    regex_compiled = RegexFSM(regex_pattern)

    print(regex_compiled.check_string("aaaaaa4uhi"))  # True
    print(regex_compiled.check_string("4uhi"))  # True
    print(regex_compiled.check_string("meow"))  # False
