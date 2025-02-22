import random
import matplotlib.pyplot as plt

def throwDice():
    return random.randint(1, 6)
    
def zeroOrNegative(number):
    return number <= 0

def getNumberOfStepsAfter100Throws():
    diceThrownTimes = 0
    stepCount = 0
    while diceThrownTimes < 100:
        diceNumber = throwDice()
        if (diceNumber == 1 or diceNumber == 2):
            if(not zeroOrNegative(stepCount)):
                stepCount -= 1
        elif (diceNumber == 3 or diceNumber == 4 or diceNumber == 5):
            stepCount += 1
        else:
            diceNumberAgain = throwDice()
            stepCount += diceNumberAgain
        
        diceThrownTimes += 1
    return stepCount


def main():
    # save all the steps taken in simulation in a list
    numberOfSimulation = 200
    allStepsTakenInSimulations = [getNumberOfStepsAfter100Throws() for i in range(numberOfSimulation)]
    print("Total steps for given simulation: ", allStepsTakenInSimulations)

    # plot the graph
    # this gives the size of the histogram frame
    plt.figure(figsize=(10, 5))
    # histogram graphs
    plt.hist(allStepsTakenInSimulations, bins=20, edgecolor='black', alpha=0.75)
    plt.xlabel('Steps')
    plt.ylabel('No of frequency')
    plt.title('Histogram of Steps in 200 Simulations of the 100 throw dice game')
    plt.show()

if __name__ == '__main__':
    main()