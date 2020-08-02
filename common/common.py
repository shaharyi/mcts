from abc import ABC, abstractmethod
import pickle
import threading
from flask import current_app


def save_in_thread(filepath, obj):
    app = current_app._get_current_object()
    t = threading.Thread(target=save_object_in_app, args=[app, filepath, obj])
    t.start()


def save_object_in_app(app, filepath, obj):
    with app.app_context():
        save_object(filepath, obj)


def save_object(filepath, obj):
    with open(filepath + '.pkl', 'wb') as output:
        pickle.dump(obj, output, -1)  # -1 is for highest protocol
    with open(filepath + '.d3.json', 'w') as output:
        s = preorder_json(obj, 0)
        output.write(s)


def load_object(filepath):
    try:
        with open(filepath + '.pkl', 'rb') as input:
            obj = pickle.load(input)
        return obj
    except IOError as error:
        print('Failed to load tree: ' + str(error))
    return None


def preorder_json(node, level):
    indent = level * 2 * ' '
    s = indent + '{\n'
    indent += 2 * ' '
    s += indent + '"name": "' + (node and str(node.action) or (node.parent and 'None' or 'Root')) + '"'
    if node.parent:
        s += ',\n'
        value = str(node.q) + ', ' + str(node.n)
        s += indent + '"value": [ ' + value + ' ]'
    if node.children:
        s += ',\n'
        s += indent + '"children": [\n'
        s += preorder_json(node.children[0], level + 2)
        for c in node.children:
            s += ',\n' + preorder_json(c, level + 2)
        s += '\n' + indent + ']\n'
    else:
        s += '\n'
    indent = level * 2 * ' '
    s += indent + '}'
    return s


class TwoPlayersAbstractGameState(ABC):

    @abstractmethod
    def game_result(self):
        """
        this property should return:

         1 if player #1 wins
        -1 if player #2 wins
         0 if there is a draw
         None if result is unknown

        Returns
        -------
        int

        """
        pass

    @abstractmethod
    def is_game_over(self):
        """
        boolean indicating if the game is over,
        simplest implementation may just be
        `return self.game_result() is not None`

        Returns
        -------
        boolean

        """
        pass

    @abstractmethod
    def move(self, action):
        """
        consumes action and returns resulting TwoPlayersAbstractGameState

        Parameters
        ----------
        action: AbstractGameAction

        Returns
        -------
        TwoPlayersAbstractGameState

        """
        pass

    @abstractmethod
    def get_legal_actions(self):
        """
        returns list of legal action at current game state
        Returns
        -------
        list of AbstractGameAction

        """
        pass


class AbstractGameAction(ABC):
    pass
