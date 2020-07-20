from math import sqrt
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

class LinRegression:
    """
    Wrapper class around scikit-learn's linear regression functionality. Per scikit-learn's documentation:

    LinearRegression fits a linear model with coefficients to minimize the residual sum of squares between the observed
    targets in the dataset, and the targets predicted by the linear approximation.
    """

    def __init__(self, attributes=None, labels=None, test_size=0.25, fit_intercept=True,
                 normalize=False, copy_X=True, n_jobs=None):
        """
        Initializes a LinearRegression object.

        The following parameters are needed to create a linear regression model:

            – attributes: a numpy array of the desired independent variables
            – labels: a numpy array of the desired dependent variables
            – test_size: the proportion of the dataset to be used for testing the model (defaults to 0.25);
            the proportion of the dataset to be used for training will be the complement of test_size
            – fit_intercept: determines whether to calculate the intercept for the model (defaults to True)
            – normalize: determines whether to normalize the dataset (defaults to False, ignored when fit_intercept
            is False)
            – copy_X: will copy the dataset's features if True (defaults to True)
            – n_jobs: the number of jobs to use for the computation (defaults to None)

        The following instance data is found after successfully running linear_regression():

            – regression: The linear regression model object
            – coefficients: an array of coefficients that most closely satisfy the linear relationship between the
            independent and dependent variables
            – intercept: the y-intercept of the regression line generated by the model
            – mean_squared_error: the average squared difference between the estimated and actual values
            – r2_score: the coefficient of determination for this linear model
            – r_score: the correlation coefficient for this linear model
        """
        self.attributes = attributes
        self.labels = labels
        self.test_size = test_size
        self.fit_intercept = fit_intercept
        self.normalize = normalize
        self.copy_X = copy_X
        self.n_jobs = n_jobs

        self.regression = None
        self.coefficients = None
        self.intercept = None
        self.mean_squared_error = None
        self.r2_score = None
        self.r_score = None

    # Accessor methods

    def get_attributes(self):
        """
        Accessor method for attributes.

        If a LinearRegression object is initialized without specifying attributes, attributes will be None.
        linear_regression() cannot be called until attributes is a numpy array of independent variables; call
        set_attributes(new_attributes) to fix this.
        """
        return self.attributes

    def get_labels(self):
        """
        Accessor method for labels.

        If a LinearRegression object is initialized without specifying labels, labels will be None.
        linear_regression() cannot be called until labels is a numpy array of dependent variables;
        call set_labels(new_labels) to fix this.
        """
        return self.labels

    def get_test_size(self):
        """
        Accessor meethod for test_size.

        Should return a number or None.
        """
        return self.test_size

    def get_fit_intercept(self):
        """
        Accessor method for fit_intercept.

        Returns a truthy/falsy value.
        """
        return self.fit_intercept

    def get_normalize(self):
        """
        Accessor method for normalize.

        Returns a truthy/falsy value.
        """
        return self.normalize

    def get_copy_X(self):
        """
        Accessor method for copy_X.

        Returns a truthy/falsy value.
        """
        return self.copy_X

    def get_n_jobs(self):
        """
        Accessor method for n_jobs.

        Should return an integer or None.
        """
        return self.n_jobs

    def get_regression(self):
        """
        Accessor method for regression.

        Will return None if linear_regression() hasn't been called, yet.
        """
        return self.regression

    def get_coefficients(self):
        """
        Accessor method for coefficients that satisfy regression model.

        Will return None if linear_regression() hasn't been called, yet.
        """
        return self.coefficients

    def get_intercept(self):
        """
        Accessor method for intercept of regression line.

        Will return None if linear_regression() hasn't been called, yet.
        """
        return self.intercept

    def get_mean_squared_error(self):
        """
        Accessor method for mean squared error of linear regression model.

        Will return None if linear_regression() hasn't been called, yet.
        """
        return self.mean_squared_error

    def get_r2_score(self):
        """
        Accessor method for coefficient of determination of linear regression model.

        Will return None if linear_regression() hasn't been called, yet.
        """
        return self.r2_score

    def get_r_score(self):
        """
        Accessor method for correlation coefficient of linear regression model.

        Will return None if linear_regression() hasn't been called, yet.
        """
        return self.r_score

    # Modifier methods

    def set_attributes(self, new_attributes=None):
        """
        Modifier method for attributes.

        Input should be a numpy array of independent variables. Defaults to None.
        """
        self.attributes = new_attributes

    def set_labels(self, new_labels=None):
        """
        Modifier method for labels.

        Input should be a numpy array of dependent variables. Defaults to None.
        """
        self.labels = new_labels

    def set_test_size(self, new_test_size=0.25):
        """
        Modifier method for test_size.

        Input should be a float between 0.0 and 1.0 or None. Defaults to 0.25. The training size will be set to the
        complement of test_size.
        """
        self.test_size = new_test_size

    def set_fit_intercept(self, new_fit_intercept=True):
        """
        Modifier method for fit_intercept.

        Input should be a truthy/falsy value. Defaults to True.
        """
        self.fit_intercept = new_fit_intercept

    def set_normalize(self, new_normalize=False):
        """
        Modifier method for normalize.

        Input should be a truthy/falsy value. Defaults to False.
        """
        self.normalize = new_normalize

    def set_copy_X(self, new_copy_X=True):
        """
        Modifier method for copy_X.

        Input should be a truthy/Falsy value. Defaults to True.
        """
        self.copy_X = new_copy_X

    def set_n_jobs(self, new_n_jobs=None):
        """
        Modifier method for n_jobs.

        Input should be an integer or None. Defaults to None.
        """
        self.n_jobs = new_n_jobs

    # Wrapper for linear regression model

    def linear_regression(self, graph_results=False):
        """
        Performs linear regression on dataset using scikit-learn's LinearRegression and updates coefficients, intercept,
        mean_squared_error, r2_score, and r_score instance data.

        To graph results, pass in graph_results=True. Note: graphing is only supported for univariate regression.
        """
        if self._check_inputs():
            # Instantiate LinearRegression() object
            self.regression = LinearRegression(fit_intercept=self.fit_intercept, normalize=self.normalize,
                                                       copy_X=self.copy_X, n_jobs=self.n_jobs)

            # Split into training and testing sets
            dataset_X_train, dataset_X_test, dataset_y_train, dataset_y_test =\
                train_test_split(self.attributes, self.labels, test_size=self.test_size)

            # Train the model and get resultant coefficients; handle exception if arguments aren't correct
            try:
                self.regression.fit(dataset_X_train, dataset_y_train)
            except Exception as e:
                print("An exception occurred while training the regression model. Check your inputs and try again.")
                print("Here is the exception message:")
                print(e)
                self.regression = None
                return

            # Get resultant coefficients and intercept of regression line
            self.coefficients = self.regression.coef_
            self.intercept = self.regression.intercept_

            # Make predictions using testing set
            y_prediction = self.regression.predict(dataset_X_test)

            # Get mean squared error, coefficient of determination, and correlation coefficient
            self.mean_squared_error = mean_squared_error(dataset_y_test, y_prediction)
            self.r2_score = r2_score(dataset_y_test, y_prediction)
            self.r_score = sqrt(self.r2_score)

            # Plot results, if desired
            if graph_results:
                self._graph_results(dataset_X_test, dataset_y_test, y_prediction)


    # Helper methods

    def _graph_results(self, X_test, y_test, y_pred):
        """
        Graphs results of linear regression with one feature. This method only graphs two-dimensional results; thus,
        only univariate regression is supported.

        graph_results() may only run after linear_regression() has successfully run.
        """
        if self.regression is None:
            print("Regression results aren't available. Have you run linear_regression() yet?")
            return

        if self.attributes.shape[1] > 1:
            print("Graphing is supported for one feature only.")
            return

        plt.scatter(X_test, y_test, color="black")
        plt.plot(X_test, y_pred, color="blue", linewidth=3)
        plt.xticks(())
        plt.yticks(())
        plt.show()

    def _check_inputs(self):
        """
        Verifies if instance data is ready for use in linear regression model.
        """

        # Check if attributes exists
        if self.attributes is None:
            print("attributes is missing; call set_attributes(new_attributes) to fix this! new_attributes should be a",
                  "populated dataset of independent variables.")
            return False

        # Check if labels exists
        if self.labels is None:
            print("labels is missing; call set_labels(new_labels) to fix this! new_labels should be a populated dataset",
                  "of dependent variables.")
            return False

        # Check if attributes and labels have same number of rows (samples)
        if self.attributes.shape[0] != self.labels.shape[0]:
            print("attributes and labels don't have the same number of rows. Make sure the number of samples in each",
                  "dataset matches!")
            return False

        # Type-checking for fit_intercept, normalize, and copy_X isn't needed; these can accept truthy/falsy values

        # Check if n_jobs is an integer or None
        if self.n_jobs is not None and not isinstance(self.n_jobs, int):
            print("n_jobs must be None or an integer; call set_n_jobs(new_n_jobs) to fix this!")
            return False

        # Check if test_size is a float or None
        if self.test_size is not None and not isinstance(self.test_size, (int, float)):
            print("test_size must be None or a number; call set_test_size(new_test_size) to fix this!")
            return False

        return True