from enum import StrEnum


class Statefull:
    '''FSMlike Base Class
    '''

    class DefaultState(StrEnum):
        undefined = 'undefined'

    def __new__(cls, *a, **k):
        cls.State = StrEnum('State', [(x, x) for x in cls.states])
        cls._state_ = None
        for state in cls.states:
            check = f'check_{state}'
            if not hasattr(cls, check):
                State = cls.State[state]
                setattr(cls, check, lambda self, STATE=State: STATE if self._state_ == STATE else None)
            process = f'process_{state}'
            if not hasattr(cls, process):
                setattr(cls, process, lambda self: None)
        return super(Statefull, cls).__new__(cls)

    def validate(self, state):
        if isinstance(state, str):
            try:
                state = getattr(self.State, state)
            except AttributeError:
                raise ValueError(f'Invalid State : {state}')

        if not isinstance(state, self.State):
            raise TypeError(f'Invalid State ! {type(state).__name__}({state})')

        return state

    @property
    def previous(self):
        if not hasattr(self, '_previous_'):
            self._previous_ = Statefull.DefaultState.undefined
        return self._previous_

    @property
    def state(self):
        for item in self.State:
            check_state = getattr(self, f'check_{item.value}')
            if state := check_state():
                self._state_ = state
                break
        else:
            self._state_ = Statefull.DefaultState.undefined

        return self._state_

    @state.setter
    def state(self, state):
        state = self.validate(state)
        self._previous_ = self._state_
        self._state_ = state

    def process(self):
        previous = self.previous.value
        state = self.state.value
        if state != previous:
            self.before_trasition(previous, state)
            self._previous_ = self._state_
            process_state = getattr(self, f'process_{state}')
            result = process_state()
            self.after_trasition(result)
            return result

    def switch(self, state):
        self.state = state
        self.process()

    def log(self, msg):
        print(f'{self.__class__.__name__} {msg}')

    def process_undefined(self):
        self.log(f' ! undefined state ! {self}')

    def before_trasition(self, previous, state):
        self.log(f'{previous} -> {state}')

    def after_trasition(self, result):
        self.log(f'{self.state} : {result}')
