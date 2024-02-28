input_file_path = 'atm.v'
output_file_path = 'output.txt'  # Change this to your desired output file name
# Read the Verilog file and write its content to a text file
with open(input_file_path, 'r') as v_file:
    verilog_content = v_file.read()

    with open(output_file_path, 'w') as txt_file:
        txt_file.write(verilog_content)
# Open the text file for reading
file_path = 'output.txt'

testFile = 'Mux.txt'


#############################################parsing
def identify_moduleName(input_file):
    with open(input_file) as file:
        for line in file:
            words = line.split()
            if 'module' in words:
                text = words[words.index('module') + 1]
                moduleName = text.split('(', )[0]
    return moduleName


def identify_inputs(input_file):
    inputs=[]
    with open(input_file, 'r') as file:
        for line in file:
            words = line.split()
            if 'input' in words:
                text = words[1]
                print(text)
                if 'wire' in words:
                    text = line.split('wire')
                    print(text)
                    text = text[1]
                if 'reg' in words:
                    text = line.split('reg')
                    print(text)
                    text = text[1]


                text = text.split(',')
                for word in text:
                    if '\n' in word:
                        word = word.replace('\n', '')
                    inputs.append(word)
                #print(text)
                #print(inputs)
                if ';' in inputs[len(inputs) - 1]:
                    inputs[len(inputs) - 1] = inputs[len(inputs) - 1].replace(';', '')
                    print(inputs)
            if 'initial' in words:
                break



    return inputs


def identify_outputs(input_file):
    outputs = []
    with open(input_file, 'r') as file:
        for line in file:
            words = line.split()
            if 'task' in words:
                break
            if 'output' in words:
                text = words[1]

                if 'reg' in line:
                    text = line.split('reg')
                    print(text)
                    text = text[1]

                text = text.split(',')
                print(text)
                for word in text:
                    outputs.append(word)
                # print()
                if ';' in outputs[len(outputs) - 1]:
                    outputs[len(outputs) - 1] = outputs[len(outputs) - 1].replace(';', '')
                if '\n' in outputs[len(outputs) - 1]:
                    outputs[len(outputs) - 1] = outputs[len(outputs) - 1].replace('\n', '')
                print(outputs)

    return outputs


inputs = identify_inputs(file_path)
outputs = identify_outputs(file_path)
moduleName = identify_moduleName(file_path)
print(outputs)
inputsModified = []
outputsModified = []

################### generation##################################
def generateModuleName(module_name, output_file):
    with open(output_file, 'w') as txt_file:
        txt_file.write('module ' + module_name + 'Test;\n')


def generatePorts(module_inputs, module_outputs, outputfile):
    with open(outputfile, 'a') as txt_file:
        for word in module_inputs:
            txt_file.write('reg ' + word + ';' + '\n')

    with open(outputfile, 'a') as txt_file:
        for word in module_outputs:
            if ' ' in word:
                txt_file.write('wire' + word + ';' + '\n')
            else:
                txt_file.write('wire' + ' ' + word + ';' + '\n')
        txt_file.write('integer i;\n')


def generateClkSignal(module_inputs, output_file):
    if 'clk' or ' clk ' or 'clk ' in module_inputs:
        with open(testFile, 'a') as txt_file:
            txt_file.write('initial ' + 'begin ' + '\n')
            txt_file.write('clk = 0;\n' + 'forever\n' + ' #1 clk=~clk;\n' + 'end' + '\n')


def generateInstance(module_inputs, module_outputs, output_file):
    with open(testFile, 'a') as txt_file:
        txt_file.write(moduleName + ' myInstance(')
        for myInput in module_inputs:
            if '[' in myInput:
                myInput = myInput.split(']')[1]

            txt_file.write(myInput + ', ')
        for i in range(len(module_outputs)):
            if '[' in module_outputs[i]:
                output = module_outputs[i].split(']')[1]
            if i == len(outputs) - 1:
                txt_file.write(module_outputs[i] + ')' + ';\n')
            else:
                txt_file.write(module_outputs[i] + ',')



rstflag=False

def generate_rst_case(module_inputs, output_file):

    if 'rst' or ' rst' or 'rst ' in inputsModified:
        rstflag=True

        with open(testFile, 'a') as txt_file:

            txt_file.write('initial begin \n')
            for myInput in inputsModified:
                txt_file.write(myInput + '=1;\n')

            txt_file.write('if(')
            for i in range(len(outputsModified)):
                if i == len(outputsModified) - 1:
                    txt_file.write(outputsModified[i] + '!=0)\n')
                else:
                    txt_file.write(outputsModified[i] + '!=0||')

            txt_file.write('$display("error");\n')
            txt_file.write('rst=0;\n')


def generateRandomized(module_inputs, output_file):

    with open(output_file, 'a') as txt_file:

        if rstflag==False:
            txt_file.write('initial begin\n')
        txt_file.write('for(i=0;i<100;i=i+1) begin\n')
        txt_file.write('#10\n')
        for myInput in module_inputs:
            if 'rst' in myInput:
                continue
            if 'clk' in myInput:
                continue
            txt_file.write(myInput + '= $random();\n')
        txt_file.write('end\n')


def generateDirected(module_inputs,output_file):
    print('how many directed cases')
    nbOfCases = int(input())
    cases = []


    for i in range(nbOfCases):
        print(f"Scenario {i + 1}")
        case = []
        for myInput in inputsModified:
            if 'clk' in myInput:
                continue
            if 'rst' in myInput:
                continue
            print(myInput + '=')

            case.append(input())
        cases.append(case)
    print(cases)

    with open(output_file, 'a') as txt_file:
        for case in cases:
            txt_file.write('#10 ')
            counter = 0
            for i in range(len(module_inputs)):
                if 'clk' in module_inputs[i]:
                    continue
                if 'rst' in module_inputs[i]:
                    continue

                txt_file.write(module_inputs[i] + ' = ' + case[counter] + ';\n')
                counter = counter + 1
            txt_file.write('\n')

        txt_file.write('#10 $stop;\nend\n')


def generateMonitor(module_inputs,module_outputs,output_file):
    with open(output_file,'a') as txt_file:
        txt_file.write('initial \n $monitor("%t:')
        for myInput in module_inputs:
            txt_file.write(myInput+' = %b,')
        for i in range(len(module_outputs)):
            if i == len(module_outputs) - 1:
                txt_file.write(module_outputs[i] + ' = %b",$time,')
            else:
                txt_file.write(module_outputs[i] + ' = %b,')

          #  txt_file.write(output + ' = %b,')
        for myInput in module_inputs:
            txt_file.write(myInput+',' )
        for i in range(len(module_outputs)):
            if i == len(module_outputs)-1:
                txt_file.write(module_outputs[i]+');\n')
            else :
                txt_file.write(module_outputs[i]+',')
        txt_file.write('endmodule')



#####################################################################
inputs = identify_inputs(file_path)
outputs = identify_outputs(file_path)
moduleName = identify_moduleName(file_path)
print(outputs)
inputsModified = []
outputsModified = []

generateModuleName(moduleName,testFile)
generatePorts(inputs,outputs,testFile)
for myInput in inputs:
    if '[' in myInput:
        myInput = myInput.split(']')[1]
    inputsModified.append(myInput)
for output in outputs:
    if '[' in output:
        output = output.split(']')[1]
    outputsModified.append(output)
print(outputsModified)
print(outputs)

generateInstance(inputsModified, outputsModified, testFile)
generateClkSignal(inputs, testFile)
generate_rst_case(inputsModified, testFile)
generateRandomized(inputsModified, testFile)
generateDirected(inputsModified, testFile)
generateMonitor(inputsModified,outputsModified,testFile)


# Read the Verilog file and write its content to a text file
with open(testFile, 'r') as txt_file:
    txt = txt_file.read()

    with open('output.v', 'w') as v_file:
        v_file.write(txt)