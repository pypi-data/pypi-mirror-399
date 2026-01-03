import math
import matplotlib.pyplot as plt
from .Generaldistribution import Distribution


class Binomial(Distribution):
    """Binomial distribution class for calculating and
    visualizing a Binomial distribution.

    Attributes:
        mean (float) representing the mean value of the distribution
        stdev (float) representing the standard deviation of the distribution
        data_list (list of floats) a list of floats to be extracted from the data file
        p (float) representing the probability of an event occurring
        n (int) the total number of trials

    """

    #  TODO: Fill out all TODOs in the functions below

    #  A binomial distribution is defined by two variables:
    #      the probability of getting a positive outcome
    #      the number of trials
    #
    #  If you know these two values, you can calculate the mean and the standard deviation
    #
    #  For example, if you flip a fair coin 25 times, p = 0.5 and n = 25
    #  You can then calculate the mean and standard deviation with the following formula:
    #      mean = p * n
    #      standard deviation = sqrt(n * p * (1 - p))

    def __init__(self, prob=0.5, size=20):

        # Store the probability of the distribution in an instance variable p
        self.p = prob
        # Store the size of the distribution in an instance variable n
        self.n = size

        # Calculate the mean and standard deviation
        self.calculate_mean()
        self.calculate_stdev()

        # Initialize the Distribution class with mean and standard deviation
        Distribution.__init__(self, self.mean, self.stdev)

    def calculate_mean(self):
        """Function to calculate the mean from p and n

        Args:
            None

        Returns:
            float: mean of the data set

        """

        # Calculate the mean of the Binomial distribution
        self.mean = self.p * self.n
        return self.mean

    def calculate_stdev(self):
        """Function to calculate the standard deviation from p and n.

        Args:
            None

        Returns:
            float: standard deviation of the data set

        """

        # Calculate the standard deviation of the Binomial distribution
        self.stdev = math.sqrt(self.n * self.p * (1 - self.p))
        return self.stdev

    def replace_stats_with_data(self):
        """Function to calculate p and n from the data set

        Args:
            None

        Returns:
            float: the p value
            float: the n value

        """

        # Update n to be the total number of data points
        self.n = len(self.data)

        # Calculate p as the number of positive outcomes divided by total trials
        self.p = sum(self.data) / len(self.data)

        # Update mean and standard deviation
        self.calculate_mean()
        self.calculate_stdev()

        return self.p, self.n

    def plot_bar(self):
        """Function to output a histogram of the instance variable data using
        matplotlib pyplot library.

        Args:
            None

        Returns:
            None
        """

        # Count occurrences of 0 and 1
        zeros = self.data.count(0)
        ones = self.data.count(1)

        # Create bar chart
        plt.bar([0, 1], [zeros, ones])
        plt.title('Bar Chart of Data')
        plt.xlabel('Outcome')
        plt.ylabel('Count')
        plt.show()

    def pdf(self, k):
        """Probability density function calculator for the gaussian distribution.

        Args:
            k (float): point for calculating the probability density function


        Returns:
            float: probability density function output
        """

        #  Calculate the probability density function for a binomial distribution
        # P(X = k) = C(n, k) * p^k * (1-p)^(n-k)

        # Calculate binomial coefficient C(n, k)
        coefficient = math.factorial(self.n) / (math.factorial(k) * math.factorial(self.n - k))

        # Calculate probability
        probability = coefficient * (self.p ** k) * ((1 - self.p) ** (self.n - k))

        return probability

    def plot_bar_pdf(self):
        """Function to plot the pdf of the binomial distribution

        Args:
            None

        Returns:
            list: x values for the pdf plot
            list: y values for the pdf plot

        """

        # Create x values from 0 to n
        x = list(range(self.n + 1))

        # Calculate y values using pdf method
        y = [self.pdf(k) for k in x]

        # Create bar chart
        plt.bar(x, y)
        plt.title('Probability Density Function of Binomial Distribution')
        plt.xlabel('Number of Successes')
        plt.ylabel('Probability')
        plt.show()

        return x, y
    def __add__(self, other):
        """Function to add together two Binomial distributions with equal p

        Args:
            other (Binomial): Binomial instance

        Returns:
            Binomial: Binomial distribution

        """

        try:
            assert self.p == other.p, "p values are not equal"
        except AssertionError as error:
            raise

        # Create new binomial distribution with combined parameters
        # p value remains the same, n values are added
        result = Binomial(prob=self.p, size=self.n + other.n)

        return result

    def __repr__(self):
        """Function to output the characteristics of the Binomial instance

        Args:
            None

        Returns:
            string: characteristics of the Gaussian

        """

        # Return string representation of the binomial distribution
        return f"mean {self.mean}, standard deviation {self.stdev}, p {self.p}, n {self.n}"
