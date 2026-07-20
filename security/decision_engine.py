class DecisionEngine:

    def __init__(self):
        pass

    def inspect(self, prediction):

        if prediction == "ATTACK":

            return "BLOCK"

        elif prediction == "NORMAL":

            return "ALLOW"

        return "BUFFER"
