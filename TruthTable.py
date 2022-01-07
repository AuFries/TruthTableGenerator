class TruthTable:

    def __init__(self):
        self.commandLst = ["!", "nand", "and", "xnor", "nor", "xor", "or"] #the list of possible boolean commands
        self.expr, self.variableDict, self.outputVar = self.getValidExpression() #the boolean expression, a dictionary associated with the values of each variable, and the output variable

    def getValidExpression(self): #Grabs a valid boolean expression from the user
        print("Enter a boolean expression in the format Y = and(A,xor(!B,C),or(A,C,D))")
        print("Possible expressions are: !, and(), nand(), or(), nor(), xor(), xnor()")
        print("-"*80)
        validExpr = False
        outputVar = None
        expr = None
        while not validExpr:
            expr = input("").replace(" ", "") #grab user input
            validExpr = True if expr[1] == "=" and expr.count("(") == expr.count(")") else False #ensure only 1 variable is assigned to the expression
            outputVar = expr[0]
            expr = expr[2:] #remove output and = chars from expression

            exprWithoutCommands = expr #remove all commands from the boolean expression so it's only variables and parens EX: (a,(b,c))
            for command in self.commandLst:
                exprWithoutCommands = exprWithoutCommands.replace(command, "")
            exprWithoutCommandsParens = exprWithoutCommands.replace("(", "").replace(")", "") #ensure no variables are directly next to eachother. Each var should be seperated by a comma.

            if not exprWithoutCommandsParens[0].isalpha(): #if the first character isn't alpha, the expression is invalid
                validExpr = False
            else: #check if the variables and commas alternate EX: a,b,c,d,e
                alpha = True
                for ch in exprWithoutCommandsParens:
                    if alpha:
                        if not ch.isalpha(): validExpr = False
                    else:
                        if ch != ",": validExpr = False
                    alpha = not alpha
                    if not validExpr:
                        break

            exprWithoutCommandsCommas = exprWithoutCommands.replace(",", "") #ensure there are least 2 variables within each parens
            #since a pair of () counts as a variable more complex checking code is necessary
            #exprWithoutCommandsCommas holds a string in the format (a(bc)(ad))
            #In the above example, the expression is valid because each interior parens holds 2 variables, and the large parens holds 3
            if exprWithoutCommandsCommas[0] != "(": ValidExpr = False
            if validExpr:
                for i, ch1 in enumerate(exprWithoutCommandsCommas):
                    if ch1 == "(":
                        varCount = 0
                        varsWithinParens = 0
                        numOpening = 1 #the number of opening brackets, which increases as more are encountered
                        j = i+1
                        encounteredAnotherOpening = False
                        while numOpening > 0 and j < len(exprWithoutCommandsCommas): #counts the number of variables within closing brackets. Each () counts as 1.
                            if exprWithoutCommandsCommas[j] == ")" and encounteredAnotherOpening:
                                varCount = (varCount + 1) - varsWithinParens
                                varsWithinParens = 0
                                numOpening -= 1
                            elif exprWithoutCommandsCommas[j] == ")":
                                numOpening -= 1
                            elif exprWithoutCommandsCommas[j] == "(":
                                encounteredAnotherOpening = True
                                numOpening += 1
                            else:
                                varCount += 1
                                varsWithinParens += 1
                            j += 1
                        if varCount < 2:
                            validExpr = False
                            break
            if not validExpr:
                print("Invalid Expression. Enter again.")
                print("-"*80)
            else:
                variableLst = sorted(set(exprWithoutCommandsParens.replace(",",""))) #create a list of all variables in the expression
                return expr, dict(zip(variableLst,[0] * len(variableLst))), outputVar #turns the list into a dictionary, return the expression, dictionary, and output variable

    def andGate(self,vars): #simulates an and gate. The result is used for nand as well
        for var in vars:
            if var == "0" or (var in self.variableDict and self.variableDict[var] == 0):
                return "0"
        return "1"

    def orGate(self,vars): #simulates an or gate. The result is used for nor as well
        for var in vars:
            if var == "1" or (var in self.variableDict and self.variableDict[var] == 1):
                return "1"
        return "0"

    def xorGate(self,vars): #simulates an xor gate. The result is used for xnor as well
        count = 0
        for var in vars:
            if var == "1" or (var in self.variableDict and self.variableDict[var] == 1):
                count += 1
        return "1" if count % 2 == 1 else "0"

    def getResult(self,expression,varLst): #returns the result for any expression and variables EX: and(x,1), or(0,1), xnor(y,z)
        if expression[:3] == "and":
            return self.andGate(varLst)
        elif expression[:2] == "or":
            return self.orGate(varLst)
        elif expression[:3] == "nor":
            return "0" if self.orGate(varLst) == "1" else "1"
        elif expression[:4] == "nand":
            return "0" if self.andGate(varLst) == "1" else "1"
        elif expression[:3] == "xor":
            return self.xorGate(varLst)
        elif expression[:4] == "xnor":
            return "0" if self.xorGate(varLst) == "1" else "1"

    def computeOutput(self): #computes the output 1 or 0 depending on the current value of the variables
        expr = self.expr
        i = 0
        while i < len(expr): #removes ! command and negates the following variable
            if expr[i] == "!":
                expr = expr[:i] + str(int(not self.variableDict[expr[i+1]])) + expr[i+2:]
                i -= 1
            i += 1

        allNums = False
        while not allNums: #while the interior still has commands ex: and(or(a,b),b) go through finding the tokens and try to evaluate them
            for command in self.commandLst[1:]: #attempt to evaluate each command
                prevIndex = 0 #holds the index which was previously attempted to evaluate
                partialExpr = expr
                if expr.count("(") in [1, 0] and expr.count(")") in [1, 0]:
                    allNums = True
                    break
                if expr.count(command) == 1: #If the is only one command of this type in the expression, set the vars to be used within the loop
                    prevIndex = expr.index(command)
                    partialExpr = expr[prevIndex:expr[prevIndex:].index(")")+prevIndex+1]

                while partialExpr.count(command) >= 1: #attempt to eval commands if there is one or more command in the partial expression. Lots of nasty string manipulation here.
                    startIndex = partialExpr.index(command)
                    curEndIndex = partialExpr.index(")") + 1 + prevIndex

                    curStartIndex = startIndex + prevIndex
                    expression = expr[curStartIndex:curEndIndex]
                    if expression.count("(") == 1 and expression.count(")") == 1: #expression can be evaluated
                        varLst = expression[expression.index("(")+1:-1].split(",") #get the variables within the parens and turn into a list
                        if all(len(var) == 1 for var in varLst): #if all variables within the expression are equal to length 1, this means there is no other commands inside the parens
                            expr = expr[:curStartIndex] + self.getResult(expression,varLst) + expr[curEndIndex:] #update the expression string with the replaced variable

                    if expr.count("(") in [1,0] and expr.count(")") in [1,0]:
                        allNums = True
                        break
                    prevIndex += startIndex + len(command)
                    partialExpr = expr[prevIndex:]

        if len(expr) == 1: #evaluate the final reults if there is only 1 command left
            return expr
        return self.getResult(expr,expr[expr.index("(")+1:-1].split(","))

    def printTable(self):
        variableDict = self.variableDict
        print(" ".join([var for var in variableDict.keys()]) + f"| {self.outputVar}")
        print("-"*(len(variableDict)*2+2))
        for i in range(2**len(variableDict)): #Go through all possible binary inputs and compute the result. Then print it to terminal
            bin = f"{i:0{len(variableDict)}b}"
            bitLst = [int(bit) for bit in bin]
            self.variableDict = dict(zip(variableDict,bitLst))
            output = self.computeOutput()
            print(" ".join([bit for bit in bin]) + f"| {output}")

if __name__ == "__main__":
    table = TruthTable()
    table.printTable()
