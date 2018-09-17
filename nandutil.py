class NANDProgram(object):
    '''Builds a NAND Program in a declarative format. Some examples will be
    shown at the end of this file. Outputs the program as a string by using the
    builtin str()'''
    def __init__(self, num_inputs, num_outputs):
        self._num_inputs = num_inputs
        self._num_outputs = num_outputs
        if num_inputs < 1 or num_outputs < 1:
            raise ValueError("Trivial NAND program")
        '''Initializes a list holding triples of our NAND program '''
        self._program = []

        '''creates allocators for unique workspace variable names.'''
        self.allocate = self.make_allocator('w')
        # You can call .allocate() to allocate generic workspace variable
        # outside the class functions.

        '''creates allocators for workspace variable names used in the helper
        functions and syntatic sugar implementations in this class. These give
        user-defined prefixes to workspace vars that may be helpful'''
        self._allocate_or_workspace_var = self.make_allocator('OR')
        self._allocate_and_workspace_var = self.make_allocator('AND')
        self._allocate_add_workspace_var = self.make_allocator('ADD')
        self._allocate_one_workspace_var = self.make_allocator('ONE')

# TODO: As you create more functions in this class to expand your syntactic
#       sugar, create an allocator for each helper function so that you can
#       have separate workspace variable names to store intermediate results
#       in each computation of the higher level functions. To make an allocator
#       pass in a string to indicate what you want the prefix of the allocator
#       to be named. Make sure that the prefixes you create are unique so that
#       the varibles are unique as well.
#
#       Feel free to make any other allocators that you feel necessary.

    def input_var(self, var_num):
        if var_num < 0 or var_num >= self._num_inputs:
            raise IndexError("Input variable is out of bounds")
        return 'x_{}'.format(var_num)

    def output_var(self, var_num):
        if var_num < 0 or var_num >= self._num_outputs:
            raise IndexError("Output variable is out of bounds")
        return 'y_{}'.format(var_num)

    @classmethod
    def make_allocator(cls, allocation_prefix):
        counter = 0

        def var_allocator():
            nonlocal counter
            new_var = (allocation_prefix + '_{}').format(counter)
            counter += 1
            return new_var
        return var_allocator

    def NAND(self, first_arg, second_arg, third_arg=None):
        '''Adds a NAND line to the end of our program
        For convenience, .NAND() is overloaded. You can call it two ways:
            .NAND(<output var name>, <input1 var name>, <input2 var name>)
            .NAND(<input1 var name>, <input2 var name>)

        The former allows YOU to specify what variable name you want to store
        the output to.

        The latter automatically allocates a new variable name to store the
        output to, which is allocated under the w_# prefix. This allows you to
        chain together mutliple NAND calls, such as:
            self.NAND('y0', self.NAND('x0','x0'), self.NAND('x1','x1'))
        '''
        output_var_name = ''
        if third_arg is None:
            output_var_name = self.allocate()
            self._program.append((output_var_name, first_arg, second_arg))
        else:
            output_var_name = first_arg
            self._program.append((first_arg, second_arg, third_arg))
        return output_var_name  # returns output var name to allow chaining

    def ONE(self, output):
        '''Adds the NAND lines to the end of our program to compute the
        constant one function'''
        intermediate_1 = self._allocate_one_workspace_var()
        self.NAND(intermediate_1, self.input_var(0), self.input_var(0))
        self.NAND(output, intermediate_1, self.input_var(0))
        return output

    def OR(self, output, var1, var2):
        '''Adds the NAND lines to the end of our program that computes
            <output> := OR(<var1>,<var2>)'''
        intermediate_1 = self._allocate_or_workspace_var()
        intermediate_2 = self._allocate_or_workspace_var()

        self.NAND(intermediate_1, var1, var1)
        self.NAND(intermediate_2, var2, var2)
        self.NAND(output, intermediate_1, intermediate_2)
        # Return a copy of the name of your output variableto allow for
        # chaining functions.
        return output

    def AND(self, output, var1, var2):
        '''Adds the NAND lines to the end of our program that computes
            <output> := AND(<var1>,<var2>)'''
        intermediate_1 = self._allocate_and_workspace_var()

        self.NAND(intermediate_1, var1, var2)
        self.NAND(output, intermediate_1, intermediate_1)
        return output

    def OR_3(self, output, var1, var2, var3):
        '''Adds the NAND lines to the end of our program that computes
            <output> := OR(<var1>, <var2>, <var3>)'''
        intermediate_1 = self._allocate_or_workspace_var()

        self.OR(intermediate_1, var1, var2)
        self.OR(output, intermediate_1, var3)
        return output

    def ADD_3(self, output1, output2, var1, var2, var3):
        '''Adds the NAND lines to the end of the program that outputs two
        binary digits representing the value of var1 + var2 + var3'''
        intermediate_0 = self._allocate_add_workspace_var()

        # TODO: implement this and other helper functions you feel necessary,
        # following a similar design as above.
        #
        # Firstly, allocate all intermediate variables used in your function by
        # using the allocator functions you define in __init__, or just use
        # self.allocate() if you don't want custom prefixes for workspace vars.
        #
        # Then, add the appropriate lines of NAND so that it computes your
        # function by calling .NAND() .OR() .AND() or any helper functions
        # that you write.
        #
        # Note that while building up your solution layer by layer is certainly
        # correct, it might make it harder to optimize its size later on, since
        # even though each component by itself uses the least gates possible,
        # the composition of the higher level components might not be optimal.
        # As such, if you are pursuing the leaderboard, you might find yourself
        # needing to reimplement some of these functions in terms of
        # lower-level constructs.

        intermediate_2 = self._allocate_add_workspace_var()

        self.NAND(intermediate_0, var1, var2)
        intermediate_1 = self.NAND(
            self._allocate_add_workspace_var(),
            self.NAND(self._allocate_add_workspace_var(), var1, intermediate_0),
            self.NAND(self._allocate_add_workspace_var(), var2, intermediate_0))

        self.NAND(intermediate_2, var3, intermediate_1)
        self.NAND(output1, self.NAND(self._allocate_add_workspace_var(), intermediate_1, intermediate_2), self.NAND(self._allocate_add_workspace_var(), var3, intermediate_2))
        self.NAND(output2, intermediate_0, intermediate_2)

    def __str__(self):
        '''Returns the NAND program as in string form, using only NAND and
        no other syntactic sugar.'''

        # checks for the case in which the number of variables assigned to is
        # less than num_outputs, which is incorrect NAND, and adds extra code
        # setting the most significant output bit to 0
        apparent_number_of_outputs = max([int(line[0][2:])
                                          for line in self._program
                                          if line[0][:2] == 'y_']) + 1
        if apparent_number_of_outputs < self._num_outputs:
            intermediate_1 = self.allocate()
            intermediate_2 = self.allocate()
            self.NAND(intermediate_1, self.input_var(0), self.input_var(0))
            self.NAND(intermediate_2, intermediate_1, self.input_var(0))
            self.NAND(self.output_var(self._num_outputs-1),
                      intermediate_2, intermediate_2)

        return '\n'.join([('{} := {} NAND {}').format(program_tuple[0],
                          program_tuple[1], program_tuple[2])
                          for program_tuple in self._program])


# TODO: Implement this function and return a string representation of its NAND
# implementation. You don't have to use the class we supplied - you could use
# other methods of building up your NAND program from scratch.
def nandsquare(n):
    '''Takes in an integer n. Outputs the string representation of a NAND prog
    that takes in inputs x_0, ..., x_{n-1} and squares it mod 2^n. The output
    will be y_0, ..., y_{n-1}. The first digit will be the least significant
    digit (ex: 110001 --> 35)'''
    # creates a blank NAND program with n inputs and n outputs.
    prog = NANDProgram(n, n)

    # now add lines to your NAND program by calling python functions like
    # prog.NAND() or prog.OR() or other helper functions. For an example, take
    # a look at the stuff after if __name__ == '__main__':

    # "compiles" your completed program as a NAND program string.
    return str(prog)
