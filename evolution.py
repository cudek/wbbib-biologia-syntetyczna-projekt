import copy
import math
import random
import statistics

def createRandomLink(inputQuantity, gatesQuantity):
    return random.randint(-inputQuantity, gatesQuantity - 1)

class NAND:
    def __init__(self, inputQuantity, gatesQuantity):
        self.inputQuantity = inputQuantity
        self.gatesQuantity = gatesQuantity
        self.id = -1
        self.inGate1 = -1
        self.inGate2 = -1
        self.inVal1 = None
        self.inVal2 = None
        self.outVal = None
        self.outGate = False
        self.isTraversed = False

    def gateToStr(self, id:int):
        return id if id >= 0 else 'A' if id == -1 else 'B'

    def __str__(self):
        return f"[{self.id}({self.gateToStr(self.inGate1)},{self.gateToStr(self.inGate2)})]"

    def __repr__(self):
        return self.__str__()



    def createGate(self, id):
        self.id = id
        self.inGate1 = createRandomLink(self.inputQuantity, self.gatesQuantity)
        self.inGate2 = createRandomLink(self.inputQuantity, self.gatesQuantity)

class Circuit:
    inputGatesQuantity = -1
    nandGatesQuantity = -1

    def __init__(self, inputGatesQuantity, nandGatesQuantity):
        self.inputGatesQuantity = inputGatesQuantity
        self.nandGatesQuantity = nandGatesQuantity
        self.gates = []
        self.fitness = 0
        self.mutations = 0

    def getOutputGate(self):
        return self.gates[self.nandGatesQuantity]

    def clean(self):
        for gate in self.gates:
            gate.isTraversed = False

    def getOutputValue(self, input:list) -> (bool, int):
        usedGates = 0
        outputGate = self.getOutputGate();
        outputValue, usedGates = self.getValue(outputGate, input, usedGates)
        self.clean()
        return outputValue, usedGates

    def getValue(self, gate:NAND, input:list, usedGates:int) -> (bool, int):
        if gate.isTraversed:
            return -1, usedGates

        gate.isTraversed = True

        if gate.inGate1 >= 0:
            output1, usedGates = self.getValue(self.gates[gate.inGate1], input, usedGates)
        else:
            output1 = input[gate.inGate1]

        if output1 == -1:
            return -1, usedGates

        if gate.inGate2 >= 0:
            output2, usedGates = self.getValue(self.gates[gate.inGate2], input, usedGates)
        else:
            output2 = input[gate.inGate2]

        if output2 == -1:
            return -1, usedGates

        return not (output1 & output2), usedGates + 1

    def getRandomGate(self) -> NAND:
        return self.gates[random.randint(0, self.nandGatesQuantity)]

    def mutate(self):
        gate = self.getRandomGate()
        self.mutations += 1
        randomLink = createRandomLink(self.inputGatesQuantity, self.nandGatesQuantity)
        if random.randint(0, 1) == 0:
            gate.inGate1 = randomLink
        else:
            gate.inGate2 = randomLink

    def init_circuit(self):
        self.gates = []

        for i in range(self.nandGatesQuantity + 1):
            gate = NAND(self.inputGatesQuantity, self.nandGatesQuantity)
            gate.createGate(i)
            self.gates.append(gate)

        #Test1
        # gate = NAND(2, 0)
        # gate.id = 0
        # gate.inGate1 = -1
        # gate.inGate2 = -2
        # self.gates.append(gate)

        #Test2
        # inputNo = 2
        # gatesNo = 4
        # gate0 = NAND(inputNo, gatesNo)
        # gate0.id = 0
        # gate0.inGate1 = -1
        # gate0.inGate2 = -1
        # self.gates.append(gate0)
        # gate1 = NAND(inputNo, gatesNo)
        # gate1.id = 1
        # gate1.inGate1 = 0
        # gate1.inGate2 = -2
        # self.gates.append(gate1)
        # gate2 = NAND(inputNo, gatesNo)
        # gate2.id = 2
        # gate2.inGate1 = -2
        # gate2.inGate2 = -2
        # self.gates.append(gate2)
        # gate3 = NAND(inputNo, gatesNo)
        # gate3.id = 3
        # gate3.inGate1 = 2
        # gate3.inGate2 = -1
        # self.gates.append(gate3)
        # gate4 = NAND(inputNo, gatesNo)
        # gate4.id = 4
        # gate4.inGate1 = 1
        # gate4.inGate2 = 3
        # self.gates.append(gate4)

    def __str__(self):
        #return f"[{self.gates}; fit: {self.fitness}; m:{self.mutations}]"
        text = "["
        for gate in self.gates:
            text += str(gate)
        return text + f",fit:{self.fitness}]"

    def __repr__(self):
        return self.__str__()


class Evolution:
    inputGatesQuantity = 2
    nandGatesQuantity = 0
    populationQuantity: int = 1
    elitesRatio = 0.0
    overwritingRatio = 0.3
    OPTIMAL_GATES = 5
    mutation_probability = 0.7
    gates_penalty = 0.2

    def __init__(self):
        self.population: list = []

    def initialize(self):
        for i in range(self.populationQuantity):
            circuit = Circuit(self.inputGatesQuantity, self.nandGatesQuantity)
            circuit.init_circuit()
            # print(circuit)
            self.population.append(circuit)

    def evaluateCircuit(self, circuit):
        inputs = [[0, 0], [0, 1], [1, 0], [1, 1]]
        expecteds = [0, 1, 1, 0]
        correct = 0
        used_gates = 0
        for input, expected in zip(inputs, expecteds):
            output, used_gates = circuit.getOutputValue(input)
            if output == -1:
                circuit.fitness = -1
                break
            else:
                correct += (output == expected)

        if circuit.fitness != -1:
            circuit.fitness = correct / len(inputs) - abs(used_gates - Evolution.OPTIMAL_GATES) * self.gates_penalty

    def sortPopulationByFitness(self) -> int:
        self.population.sort(key=lambda p: p.fitness)
        bestFitness = self.population[-1].fitness
        return bestFitness

    def getAverageFitness(self) -> int:
        return statistics.mean(p.fitness for p in self.population)

    def getQuantityFromPopulation(self, ratio):
        return math.floor(len(self.population) * ratio)

    def getBest(self):
        return self.population[-1]

    def naturalSelection(self):
        overwritingQuantity = self.getQuantityFromPopulation(self.overwritingRatio)
        for i in range(0, overwritingQuantity):
            self.population[i] = copy.deepcopy(self.population[-i - 1])

    def isMutating(self):
        return random.random() <= self.mutation_probability

    def mutate(self):
        elitesNumber = self.getQuantityFromPopulation(self.elitesRatio)
        for i in range(0, len(self.population) - elitesNumber):
            circuit = self.population[i]
            if self.isMutating():
                circuit.mutate()

    def evaluate(self):
        for circuit in self.population:
            self.evaluateCircuit(circuit)


class Simulation:
    epochs = -1
    verbose = False

    def learn(self, evolution: Evolution):
        evolution.initialize()
        evolution.evaluate()
        evolution.sortPopulationByFitness()
        if self.verbose:
            print("Best circuits:")
            print(f"0: {evolution.getBest()}")

        bestFitnesses = []
        avgFitnesseses = []

        for epoch in range(0, self.epochs):
            evolution.evaluate()
            bestFitness = evolution.sortPopulationByFitness()
            bestFitnesses.append(bestFitness)
            avgFitnesseses.append(evolution.getAverageFitness())
            evolution.naturalSelection()
            evolution.mutate()

            if (epoch > 0 and epoch % (self.epochs / 10) == 0):
                if self.verbose:
                    print(f"{epoch}: {evolution.getBest()}")
                else:
                    print(f"\rEpoch: {epoch}", end='')

        if self.verbose:
            print(f"{self.epochs}: {evolution.getBest()}")

        return bestFitnesses, avgFitnesseses

# evolution = Evolution()
# evolution.nandGatesQuantity = 10
# evolution.inputGatesQuantity = 2
# evolution.populationQuantity = 50
# evolution.elitesRatio = 0.0 #procent nie mutowanych najlepszych
# evolution.overwritingRatio = 0.2 #procent nadpisywanych najgorszych
# evolution.mutation_probability = 0.7 #szansa na mutację
# evolution.gates_penalty = 0.0 #jak bardzo każemy za nieoptymalną liczbę bramek
#
#
# simulation = Simulation()
# simulation.epochs = 1000
# best_fitness, avg_fitness = simulation.learn(evolution)