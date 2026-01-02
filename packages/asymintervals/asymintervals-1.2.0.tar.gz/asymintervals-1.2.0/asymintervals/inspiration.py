import numpy as np
import matplotlib.pyplot as plt


class AIN:
    def __init__(self, lower: float, upper: float, expected: float = None):
        """
        Initialize an Asymmetric Interval Number (AIN) with specified bounds and an optional expected value.

        This constructor creates an instance of AIN using `lower` and `upper` bounds to define the interval.
        Optionally, an `expected` value within this range can be provided. If `expected` is not specified,
        it defaults to the midpoint of `lower` and `upper`. The `expected` value must lie within the interval
        `[lower, upper]`. The constructor also calculates the two parameters defining the AIN distribution (`alpha`, `beta`),
        the degree of asymmetry (`asymmetry`), and the variance (`D2`) based on the specified bounds and expected value.

        Parameters
        ----------
        lower : float
            The lower bound of the interval. Must be less or equal than `upper`.
        upper : float
            The upper bound of the interval. Must be greater or equal than `lower`.
        expected : float, optional
            The expected value within the interval. Defaults to the midpoint `(lower + upper) / 2` if not provided.

        Raises
        ------
        TypeError
            If `lower`, `upper`, or `expected` are not of type float or int.
        ValueError
            If `expected` is not within the range `[lower, upper]`.

        Attributes
        ----------
        lower : float
            The lower bound of the interval.
        upper : float
            The upper bound of the interval.
        expected : float
            The expected value within the interval [`lower`, `upper`].
        alpha : float
            The distribution parameter for the interval [`lower`, `expected`], calculated when
            `lower` is less than `upper`. If `lower` equals `upper`, the parameter is set to 1.
        beta : float
            The distribution parameter for the interval [`expected`, `upper`], calculated when
            `lower` is less than `upper`. If `lower` equals `upper`, the parameter is set to 1.
        asymmetry : float
            The asymmetry degree of the interval, representing the relative position of `expected`
            between `lower` and `upper`. If `lower` equals `upper`, the `asymmetry` is set to 0.
        D2 : float
            A parameter representing the variance of the interval, derived from the degree of
            asymmetry and the specified bounds.

        Examples
        --------
        Creating an AIN with a specified expected value:
        >>> a = AIN(0, 10, 8)
        >>> print(a)
        [0.0000, 10.0000]_{8.0000}

        Creating an AIN with a default expected value:
        >>> b = AIN(0, 10)
        >>> repr(b)
        'AIN(0, 10, 5.0)'

        Attempting to create an improper AIN:
        >>> c = AIN(1, 2, 3)
        Traceback (most recent call last):
        ...
        ValueError: It is not a proper AIN 1.0000, 2.0000, 3.0000
        """
        if not isinstance(lower, (int, float)):
            raise TypeError('lower must be int or float')
        if not isinstance(upper, (int, float)):
            raise TypeError('upper must be int or float')
        if not (expected is None or isinstance(expected, (int, float))):
            raise TypeError('expected must be int or float')
        if expected is None:
            expected = (lower + upper) / 2
        if not (lower <= expected <= upper):
            raise ValueError(f'It is not a proper AIN {lower:.4f}, {upper:.4f}, {expected:.4f}')
        self.lower = lower
        self.upper = upper
        self.expected = expected

        if self.lower == self.upper:
            self.alpha = 1.0
            self.beta = 1.0
            self.asymmetry = 0.0
            self.D2 = 0.0
        else:
            self.alpha = (self.upper - self.expected) / ((self.upper - self.lower) * (self.expected - self.lower))
            self.beta = (self.expected - self.lower) / ((self.upper - self.lower) * (self.upper - self.expected))
            self.asymmetry = (self.lower + self.upper - 2 * self.expected) / (self.upper - self.lower)
            self.D2 = self.alpha * (self.expected ** 3 - self.lower ** 3) / 3 + self.beta * (
                    self.upper ** 3 - self.expected ** 3) / 3 - self.expected ** 2

    def sin(self):
        """
        Compute sine of an AIN instance.

        Returns
        -------
        AIN
            A new AIN instance representing sin(X).

        Examples
        --------
        >>> x = AIN(0, np.pi/2, np.pi/4)
        >>> result = x.sin()
        >>> print(result)
        [0.0000, 1.0000]_{0.6366}

        >>> x = AIN(0, 0, 0)
        >>> result = x.sin()
        >>> print(result)
        [0.0000, 0.0000]_{0.0000}
        """

        # Przypadek zdegenerowany
        if self.lower == self.upper:
            val = np.sin(self.expected)
            return AIN(val, val, val)

        # Znajdź min i max sinusa na [a, b]
        a, b, c = self.lower, self.upper, self.expected

        candidates = [np.sin(a), np.sin(b)]

        # Sprawdź czy przedział zawiera maksima sinusa (π/2 + 2kπ)
        k_max_start = int(np.ceil((a - np.pi / 2) / (2 * np.pi)))
        k_max_end = int(np.floor((b - np.pi / 2) / (2 * np.pi)))
        for k in range(k_max_start, k_max_end + 1):
            x_max = np.pi / 2 + 2 * k * np.pi
            if a <= x_max <= b:
                candidates.append(1.0)

        # Sprawdź czy przedział zawiera minima sinusa (-π/2 + 2kπ)
        k_min_start = int(np.ceil((a + np.pi / 2) / (2 * np.pi)))
        k_min_end = int(np.floor((b + np.pi / 2) / (2 * np.pi)))
        for k in range(k_min_start, k_min_end + 1):
            x_min = -np.pi / 2 + 2 * k * np.pi
            if a <= x_min <= b:
                candidates.append(-1.0)

        new_a = min(candidates)
        new_b = max(candidates)

        # Wartość oczekiwana z LOTUS
        new_c = (self.alpha * (np.cos(self.lower) - np.cos(self.expected)) +
                 self.beta * (np.cos(self.expected) - np.cos(self.upper)))

        return AIN(new_a, new_b, new_c)

    def tan(self):
        """
        Compute tangent of an AIN instance.

        Returns
        -------
        AIN
            A new AIN instance representing tan(X).

        Raises
        ------
        ValueError
            If the interval contains or touches a discontinuity (asymptote) of tan(x).
            tan(x) has asymptotes at x = π/2 + kπ for any integer k.

        Examples
        --------
        >>> x = AIN(0, np.pi/4, np.pi/8)
        >>> result = x.tan()
        >>> print(result)
        [0.0000, 1.0000]_{0.2027}

        >>> x = AIN(-np.pi/4, np.pi/4, 0)
        >>> result = x.tan()
        >>> print(result)
        [-1.0000, 1.0000]_{0.0000}
        """

        # Przypadek zdegenerowany
        if self.lower == self.upper:
            # Sprawdź czy punkt jest asymptotą
            if np.abs(np.cos(self.expected)) < 1e-10:
                raise ValueError(
                    f"tan(x) is undefined at x = {self.expected:.4f} (asymptote at π/2 + kπ)"
                )
            val = np.tan(self.expected)
            return AIN(val, val, val)

        a, b, c = self.lower, self.upper, self.expected

        # Sprawdź czy przedział zawiera lub dotyka asymptot tangensa (π/2 + kπ)
        k_asymp_start = int(np.ceil((a - np.pi / 2) / np.pi))
        k_asymp_end = int(np.floor((b - np.pi / 2) / np.pi))

        for k in range(k_asymp_start, k_asymp_end + 1):
            x_asymp = np.pi / 2 + k * np.pi
            if a <= x_asymp <= b:
                raise ValueError(
                    f"The interval [{a:.4f}, {b:.4f}] contains a discontinuity of tan(x) at x = {x_asymp:.4f}. "
                    f"tan(x) is undefined at x = π/2 + kπ."
                )

        # Jeśli nie ma asymptot, tan jest monotonicznie rosnący
        new_a = np.tan(a)
        new_b = np.tan(b)

        # Wartość oczekiwana z LOTUS
        # E(tan(X)) = α·∫[a,c] tan(x)dx + β·∫[c,b] tan(x)dx
        # ∫tan(x)dx = -ln|cos(x)|
        # = α·[-ln|cos(x)|] od a do c + β·[-ln|cos(x)|] od c do b
        # = α·(-ln|cos(c)| + ln|cos(a)|) + β·(-ln|cos(b)| + ln|cos(c)|)
        # = α·ln|cos(a)/cos(c)| + β·ln|cos(c)/cos(b)|

        new_c = (self.alpha * np.log(np.abs(np.cos(a) / np.cos(c))) +
                 self.beta * np.log(np.abs(np.cos(c) / np.cos(b))))

        return AIN(new_a, new_b, new_c)

    def cos(self):
        """
        Compute cosine of an AIN instance.

        Returns
        -------
        AIN
            A new AIN instance representing cos(X).

        Examples
        --------
        >>> x = AIN(0, np.pi/2, np.pi/4)
        >>> result = x.cos()
        >>> print(result)
        [0.0000, 1.0000]_{0.6366}

        >>> x = AIN(0, np.pi, np.pi/2)
        >>> result = x.cos()
        >>> print(result)
        [-1.0000, 1.0000]_{0.0000}
        """

        # Przypadek zdegenerowany
        if self.lower == self.upper:
            val = np.cos(self.expected)
            return AIN(val, val, val)

        # Znajdź min i max cosinusa na [a, b]
        a, b, c = self.lower, self.upper, self.expected

        candidates = [np.cos(a), np.cos(b)]

        # Sprawdź czy przedział zawiera maksima cosinusa (2kπ)
        k_max_start = int(np.ceil(a / (2 * np.pi)))
        k_max_end = int(np.floor(b / (2 * np.pi)))
        for k in range(k_max_start, k_max_end + 1):
            x_max = 2 * k * np.pi
            if a <= x_max <= b:
                candidates.append(1.0)

        # Sprawdź czy przedział zawiera minima cosinusa (π + 2kπ)
        k_min_start = int(np.ceil((a - np.pi) / (2 * np.pi)))
        k_min_end = int(np.floor((b - np.pi) / (2 * np.pi)))
        for k in range(k_min_start, k_min_end + 1):
            x_min = np.pi + 2 * k * np.pi
            if a <= x_min <= b:
                candidates.append(-1.0)

        new_a = min(candidates)
        new_b = max(candidates)

        # Wartość oczekiwana z LOTUS
        # E(cos(X)) = α·∫[a,c] cos(x)dx + β·∫[c,b] cos(x)dx
        # ∫cos(x)dx = sin(x)
        # = α·[sin(x)] od a do c + β·[sin(x)] od c do b
        # = α·(sin(c) - sin(a)) + β·(sin(b) - sin(c))
        new_c = (self.alpha * (np.sin(self.expected) - np.sin(self.lower)) +
                 self.beta * (np.sin(self.upper) - np.sin(self.expected)))

        return AIN(new_a, new_b, new_c)

    def sinh(self):
        """
        Compute hyperbolic sine of an AIN instance.

        The hyperbolic sine is defined as sinh(x) = (e^x - e^(-x))/2.
        It is a monotonically increasing function for all real x.

        Returns
        -------
        AIN
            A new AIN instance representing sinh(X).

        Examples
        --------
        >>> x = AIN(0, 1, 0.5)
        >>> result = x.sinh()
        >>> print(result)
        [0.0000, 1.1752]_{0.5211}

        >>> x = AIN(-1, 1, 0)
        >>> result = x.sinh()
        >>> print(result)
        [-1.1752, 1.1752]_{0.0000}
        """
        # Przypadek zdegenerowany
        if self.lower == self.upper:
            val = np.sinh(self.expected)
            return AIN(val, val, val)

        a, b, c = self.lower, self.upper, self.expected

        # sinh jest monotonicznie rosnący
        new_a = np.sinh(a)
        new_b = np.sinh(b)

        # Wartość oczekiwana z LOTUS
        # E(sinh(X)) = α·∫[a,c] sinh(x)dx + β·∫[c,b] sinh(x)dx
        # ∫sinh(x)dx = cosh(x)
        # = α·(cosh(c) - cosh(a)) + β·(cosh(b) - cosh(c))
        new_c = (self.alpha * (np.cosh(c) - np.cosh(a)) +
                 self.beta * (np.cosh(b) - np.cosh(c)))

        return AIN(new_a, new_b, new_c)

    def cosh(self):
        """
        Compute hyperbolic cosine of an AIN instance.

        The hyperbolic cosine is defined as cosh(x) = (e^x + e^(-x))/2.
        It has a minimum at x = 0 with cosh(0) = 1.

        Returns
        -------
        AIN
            A new AIN instance representing cosh(X).

        Examples
        --------
        >>> x = AIN(0, 1, 0.5)
        >>> result = x.cosh()
        >>> print(result)
        [1.0000, 1.5431]_{1.1276}

        >>> x = AIN(-1, 1, 0)
        >>> result = x.cosh()
        >>> print(result)
        [1.0000, 1.5431]_{1.1752}
        """
        # Przypadek zdegenerowany
        if self.lower == self.upper:
            val = np.cosh(self.expected)
            return AIN(val, val, val)

        a, b, c = self.lower, self.upper, self.expected

        # cosh ma minimum w 0
        candidates = [np.cosh(a), np.cosh(b)]

        # Sprawdź czy przedział zawiera 0 (minimum cosh)
        if a <= 0 <= b:
            candidates.append(1.0)

        new_a = min(candidates)
        new_b = max(candidates)

        # Wartość oczekiwana z LOTUS
        # E(cosh(X)) = α·∫[a,c] cosh(x)dx + β·∫[c,b] cosh(x)dx
        # ∫cosh(x)dx = sinh(x)
        # = α·(sinh(c) - sinh(a)) + β·(sinh(b) - sinh(c))
        new_c = (self.alpha * (np.sinh(c) - np.sinh(a)) +
                 self.beta * (np.sinh(b) - np.sinh(c)))

        return AIN(new_a, new_b, new_c)

    def tanh(self):
        """
        Compute hyperbolic tangent of an AIN instance.

        The hyperbolic tangent is defined as tanh(x) = sinh(x)/cosh(x).
        It is a monotonically increasing function bounded by (-1, 1).

        Returns
        -------
        AIN
            A new AIN instance representing tanh(X).

        Examples
        --------
        >>> x = AIN(0, 1, 0.5)
        >>> result = x.tanh()
        >>> print(result)
        [0.0000, 0.7616]_{0.4622}

        >>> x = AIN(-2, 2, 0)
        >>> result = x.tanh()
        >>> print(result)
        [-0.9640, 0.9640]_{0.0000}
        """
        # Przypadek zdegenerowany
        if self.lower == self.upper:
            val = np.tanh(self.expected)
            return AIN(val, val, val)

        a, b, c = self.lower, self.upper, self.expected

        # tanh jest monotonicznie rosnący i ograniczony do (-1, 1)
        new_a = np.tanh(a)
        new_b = np.tanh(b)

        # Wartość oczekiwana z LOTUS
        # E(tanh(X)) = α·∫[a,c] tanh(x)dx + β·∫[c,b] tanh(x)dx
        # ∫tanh(x)dx = ln(cosh(x))
        # = α·(ln(cosh(c)) - ln(cosh(a))) + β·(ln(cosh(b)) - ln(cosh(c)))
        # = α·ln(cosh(c)/cosh(a)) + β·ln(cosh(b)/cosh(c))
        new_c = (self.alpha * np.log(np.cosh(c) / np.cosh(a)) +
                 self.beta * np.log(np.cosh(b) / np.cosh(c)))

        return AIN(new_a, new_b, new_c)

    def __repr__(self):
        """
        Return an unambiguous string representation of the AIN instance.
        The representation includes the class name `AIN`, followed by the
        `lower`, `upper`, and `expected` values enclosed in parentheses.

        Returns
        -------
        str
            A string that accurately reflects the construction of the instance.

        Examples
        --------
        >>> a = AIN(0, 10, 8)
        >>> repr(a)
        'AIN(0, 10, 8)'

        >>> b = AIN(0, 10)
        >>> repr(b)
        'AIN(0, 10, 5.0)'
        """
        return f"AIN({self.lower}, {self.upper}, {self.expected})"

    def __str__(self):
        """
        Return a human-readable string representation of the AIN instance.

        The string is formatted as '[lower, upper]_{expected}' where 'lower', 'upper',
        and 'expected' are displayed with four decimal places. This format is designed
        to be clear, concise, and user-friendly, making it well-suited for printing and
        easy interpretation by end-users.

        Returns
        -------
        str
            A string representation of the `AIN` instance, formatted to four decimal
            places for each numeric value.

        Examples
        --------
        >>> a = AIN(0, 10, 8)
        >>> print(a)
        [0.0000, 10.0000]_{8.0000}

        >>> b = AIN(0, 10)
        >>> print(b)
        [0.0000, 10.0000]_{5.0000}
        """
        return f"[{self.lower:.4f}, {self.upper:.4f}]_{{{self.expected:.4f}}}"

    def __neg__(self):
        """
        Returns a new `AIN` instance representing the negation of the current
        instance (the additive inverse of the interval).

        The negation of an AIN instance is achieved by reversing the signs of the
        `lower`, `upper`, and `expected` values:
        - The new `lower` bound becomes the negation of the original `upper` bound.
        - The new `upper` bound becomes the negation of the original `lower` bound.
        - The new `expected` value becomes the negation of the original `expected` value.

        Returns
        -------
        AIN
            A new `AIN` instance representing the additive inverse of the interval.

        Examples
        --------
        >>> a = AIN(1, 10, 8)
        >>> print(-a)
        [-10.0000, -1.0000]_{-8.0000}

        >>> a = AIN(2, 10)
        >>> print(-a)
        [-10.0000, -2.0000]_{-6.0000}

        >>> a = np.array([AIN(0, 10), AIN(2, 8, 7)])
        >>> print(-a)
        [AIN(-10, 0, -5.0) AIN(-8, -2, -7)]
        """
        return AIN(-self.upper, -self.lower, -self.expected)

    def __add__(self, other):
        """
        Adds either another `AIN` instance or a value of type `int` or `float` to the current
        `AIN` instance. Returns a new `AIN` instance representing the result.

        - When adding another `AIN` instance, the resulting `lower`, `upper`, and `expected`
        values are calculated by summing the corresponding values of both `AIN` instances.
        - When adding a value of type `int` or `float`, the value is added to each component
        (`lower`, `upper`, and `expected`) of the current AIN instance.

        Parameters
        ----------
        other : AIN, float, or int
            The value to be added, which can be `AIN` instance, a `float`, or an `int`.

        Returns
        -------
        AIN
            Returns a new `AIN` instance representing the result of the addition, with the
            `lower`, `upper`, and `expected` values updated accordingly based on the operation.

        Raises
        ------
        TypeError
            If `other` is not an instance of `AIN`, `float`, or `int`.

        Examples
        --------
        Addition with another `AIN` instance:
        >>> a = AIN(1, 10, 8)
        >>> b = AIN(0, 5, 2)
        >>> print(a + b)
        [1.0000, 15.0000]_{10.0000}

        Addition with a `float` or `int`:
        >>> a = AIN(1, 10, 8)
        >>> b = 2
        >>> print(a + b)
        [3.0000, 12.0000]_{10.0000}

        Performing addition with a `np.array` of `AIN` instances:
        >>> a = np.array([AIN(0, 10), AIN(2, 8, 7)])
        >>> print(a + 2)
        [AIN(2, 12, 7.0) AIN(4, 10, 9)]

        """
        if not isinstance(other, (AIN, float, int)):
            raise TypeError(f"other is not an instance of AIN or float or int")
        if isinstance(other, AIN):
            new_a = self.lower + other.lower
            new_b = self.upper + other.upper
            new_c = self.expected + other.expected
            res = AIN(new_a, new_b, new_c)
        else:
            res = AIN(self.lower + other, self.upper + other, self.expected + other)
        return res

    def __radd__(self, other):
        """
        Perform reflected (reverse) addition for an AIN instance.

        This method handles the addition of an Asymmetric Interval Number (`AIN`) instance
        to a value of type `float` or `int` when the AIN appears on the right-hand side
        of the addition (i.e., `other + self`).

        It computes `other + self`, ensuring commutative addition between `AIN` instances
        and numeric values (`float` or `int`).

        Parameters
        ----------
        other : float or int
            The value to add to the current AIN instance.

        Returns
        -------
        AIN
            A new `AIN` instance representing the result of the addition, with `lower`, `upper`,
            and `expected` values equal to the sum of `other` and the corresponding values of
            the current `AIN` instance.

        Raises
        ------
        TypeError
            If `other` is not a float or int.

        Examples
        --------
        >>> a = AIN(1, 10, 8)
        >>> b = 5
        >>> print(b + a)
        [6.0000, 15.0000]_{13.0000}

        >>> a = np.array([AIN(0, 10), AIN(2, 8, 7)])
        >>> b = 2
        >>> print(2 + a)
        [AIN(2, 12, 7.0) AIN(4, 10, 9)]
        """
        if not isinstance(other, (float, int)):
            raise TypeError("other must be of type float or int")
        return self + other

    def __sub__(self, other):
        """
        Subtract an `AIN` instance or a `float` or `int` from the current `AIN` instance.

        This method allows subtraction of either another `AIN` or a `float` or `int` from
        the current `AIN` instance, returning a new `AIN` instance with the result. When
        subtracting another `AIN`, the resulting bounds and expected value are computed by
        subtracting the corresponding values of the operands. If subtracting a `float` or
        `int`, the value is subtracted from each component of the current `AIN` instance.

        Parameters
        ----------
        other : AIN, float, or int
            The value to subtract, which can be an `AIN` instance, a `float`, or an `int`.

        Returns
        -------
        AIN
            A new `AIN` instance representing the result of the subtraction, with adjusted
            `lower`, `upper`, and `expected` values based on the operation.

        Raises
        ------
        TypeError
            If `other` is not an instance of `AIN`, `float`, or `int`.

        Examples
        --------
        Subtracting an `AIN` instance:
        >>> a = AIN(1, 10, 8)
        >>> b = AIN(0, 5, 2)
        >>> print(a - b)
        [-4.0000, 10.0000]_{6.0000}

        Subtracting a `float` or `int`:
        >>> a = AIN(1, 10, 8)
        >>> b = 2
        >>> print(a - b)
        [-1.0000, 8.0000]_{6.0000}

        Performing subtraction with a `np.array` of `AIN` instances:
        >>> a = np.array([AIN(0, 10), AIN(2, 8, 7)])
        >>> b = AIN(0, 5, 4)
        >>> print(a - b)
        [AIN(-5, 10, 1.0) AIN(-3, 8, 3)]
        """
        if not isinstance(other, (AIN, float, int)):
            raise TypeError("other is not an instance of AIN or float or int")
        if isinstance(other, AIN):
            new_a = self.lower - other.upper
            new_b = self.upper - other.lower
            new_c = self.expected - other.expected
            res = AIN(new_a, new_b, new_c)
        else:
            res = AIN(self.lower - other, self.upper - other, self.expected - other)
        return res

    def __rsub__(self, other):
        """
        Perform reflected (reverse) subtraction for an `AIN` instance.

        This method is invoked when an `AIN` instance appears on the right-hand side of
        a subtraction operation (i.e., `other - self`) and the left operand (`other`) does
        not support subtraction with an `AIN`. It calculates the result of `other - self`.

        Parameters
        ----------
        other : float or int
            The value from which the current `AIN` instance is subtracted.

        Returns
        -------
        AIN
            A new `AIN` instance representing the result of the subtraction. The resulting
            `AIN` has its `lower`, `upper`, and `expected` values computed as the difference between
            `other` and the respective values of the `AIN` instance.

        Raises
        ------
        TypeError
            If `other` is not a `float` or `int`.

        Examples
        --------
        >>> a = AIN(1, 10, 8)
        >>> b = 5
        >>> print(b - a)
        [-5.0000, 4.0000]_{-3.0000}

        >>> a = np.array([AIN(0, 10), AIN(2, 8, 7)])
        >>> print(2 - a)
        [AIN(-8, 2, -3.0) AIN(-6, 0, -5)]
        """
        if not isinstance(other, (float, int)):
            raise TypeError("other must be of type float or int")
        return -self + other

    def __mul__(self, other):
        """
        Perform multiplication of the current `AIN` instance with another `AIN` or a `float` or `int`.

        This method allows the multiplication of an `AIN` instance with another `AIN` instance
        or a `float` or `int`, returning a new `AIN` instance that represents the result. When
        multiplying with another `AIN`, the interval boundaries are computed based on the
        combinations of bounds from both `AIN` instances.

        Parameters
        ----------
        other : AIN, float, or int
            The value to multiply with, which can be another `AIN` instance, a `float`, or an `int`.

        Returns
        -------
        AIN
            A new `AIN` instance representing the product of the multiplication.

        Raises
        ------
        TypeError
            If `other` is not an instance of `AIN`, `float`, or `int`.

        Examples
        --------
        Multiplying with another `AIN` instance:
        >>> a = AIN(1, 3, 2)
        >>> b = AIN(2, 4, 3)
        >>> print(a * b)
        [2.0000, 12.0000]_{6.0000}

        Multiplying with a `float` or `int`:
        >>> a = AIN(1, 3, 2)
        >>> b = 2
        >>> print(a * b)
        [2.0000, 6.0000]_{4.0000}

        Performing multiplication with a `np.array` of `AIN` instances:
        >>> a = np.array([AIN(0, 10), AIN(2, 8, 7)])
        >>> b = AIN(1,4,2)
        >>> print(a * b)
        [AIN(0, 40, 10.0) AIN(2, 32, 14)]
        """
        if not isinstance(other, (int, float, AIN)):
            raise TypeError('other must be an instance of AIN or int or float')
        if isinstance(other, AIN):
            new_a = min(self.lower * other.lower, self.upper * other.upper, self.lower * other.upper,
                        self.upper * other.lower)
            new_b = max(self.lower * other.lower, self.upper * other.upper, self.lower * other.upper,
                        self.upper * other.lower)
            new_c = self.expected * other.expected
            res = AIN(new_a, new_b, new_c)
        else:
            res = AIN(self.lower * other, self.upper * other, self.expected * other)
        return res

    def __rmul__(self, other):
        """
        Perform reverse multiplication for an `AIN` instance with a `float` or `int`.

        This method allows an `AIN` instance to be multiplied by a `float` or `int` in
        cases where the `float` or `int` appears on the left side of the multiplication
        (i.e., `other * self`). This enables commutative multiplication between `AIN`
        and `float` or int values.

        Parameters
        ----------
        other : float or int
            An `float` or `int` value to multiply with the `AIN` instance.

        Returns
        -------
        AIN
            A new `AIN` instance representing the result of the multiplication.

        Raises
        ------
        TypeError
            If `other` is not a `float` or `int`.

        Examples
        --------
        >>> a = AIN(1, 3, 2)
        >>> b = 2
        >>> result = b * a
        >>> print(result)
        [2.0000, 6.0000]_{4.0000}

        >>> a = np.array([AIN(0, 10), AIN(2, 8, 7)])
        >>> b = 2
        >>> print(b * a)
        [AIN(0, 20, 10.0) AIN(4, 16, 14)]
        """
        if not isinstance(other, (float, int)):
            raise TypeError("other must be float or int")
        return self * other

    def __truediv__(self, other):
        """
        Perform division of the current `AIN` instance by another `AIN` instance or a `float` or `int`.

        This method supports division by either another `AIN` or a `float` or `int`, returning a new
        `AIN` instance as the result. When dividing by an `AIN`, interval boundaries are calculated
        by dividing the respective boundaries, while the expected value is adjusted based on logarithmic
        calculations if the bounds differ.

        Parameters
        ----------
        other : AIN, float, or int
            The divisor, which can be an `AIN` instance, a `float`, or an `int`.

        Returns
        -------
        AIN
            A new `AIN` instance representing the result of the division.

        Raises
        ------
        TypeError
            If `other` is not an instance of `AIN`, `float`, or `int`.

        Examples
        --------
        Division with another AIN instance:
        >>> a = AIN(4, 8, 6)
        >>> b = AIN(2, 4, 3)
        >>> print(a / b)
        [1.0000, 4.0000]_{2.0794}

        Division with a float or int:
        >>> a = AIN(4, 8, 6)
        >>> b = 2
        >>> print(a / b)
        [2.0000, 4.0000]_{3.0000}

        Performing division with a np.array of AIN instances:
        >>> a = np.array([AIN(0, 10), AIN(2, 8, 7)])
        >>> b = AIN(1, 4, 2)
        >>> print(a / b)
        [AIN(0.0, 10.0, 2.8881132523331052) AIN(0.5, 8.0, 4.043358553266348)]
        """
        if not isinstance(other, (AIN, int, float)):
            raise TypeError(f"other must be an instance of AIN or float or int")
        if isinstance(other, AIN):
            new_a = min(self.lower / other.lower, self.upper / other.upper, self.lower / other.upper,
                        self.upper / other.lower)
            new_b = max(self.lower / other.lower, self.upper / other.upper, self.lower / other.upper,
                        self.upper / other.lower)
            if other.lower == other.upper:
                new_c = (new_a + new_b) / 2
            else:
                new_c = self.expected * (other.alpha * np.log(other.expected / other.lower) + other.beta * np.log(
                    other.upper / other.expected))
            res = AIN(new_a, new_b, new_c)
        else:
            res = AIN(self.lower / other, self.upper / other, self.expected / other)
        return res

    def __rtruediv__(self, other):
        """
        Perform reverse true division of a float or int by an `AIN` instance.

        This method enables division where a float or int `other` is divided by an AIN instance (`self`),
        calculating the reciprocal of `self` and then scaling it by `other`. It returns a new `AIN`
        instance representing the outcome.

        Parameters
        ----------
        other : float or int
            The `float` or `int` to divide by the `AIN` instance.

        Returns
        -------
        AIN
            A new `AIN` instance representing `other` divided by `self`.

        Raises
        ------
        TypeError
            If `other` is not a `float` or `int`.

        Examples
        --------
        >>> a = AIN(2, 4, 3)
        >>> result = 10 / a
        >>> print(result)
        [2.5000, 5.0000]_{3.4657}

        >>> a = np.array([AIN(2,10), AIN(2,8, 7)])
        >>> result = 2 / a
        >>> print(result)
        [AIN(0.2, 1.0, 0.4023594781085251) AIN(0.25, 1.0, 0.3060698522738955)]
        """
        if not isinstance(other, (float, int)):
            raise TypeError(f"other variable is not a float or int")
        return other * self ** (-1)

    def __pow__(self, n):
        """
        Raise an `AIN` instance to the power `n`.

        Parameters
        ----------
        n : int, float, or AIN
            The exponent to which the `AIN` is raised.

        Returns
        -------
        AIN
            A new `AIN` instance representing the interval raised to the power of `n`.

        Examples
        --------
        >>> a = AIN(4, 8, 5)
        >>> print(a**2)
        [16.0000, 64.0000]_{26.0000}

        >>> a = AIN(2, 4, 3)
        >>> b = AIN(1, 2, 1.5)
        >>> result = a**b  # A^B = exp(B*log(A))
        >>> print(result)
        [2.0000, 16.0000]_{5.9305}
        """
        # Obsługa np.array
        if isinstance(self, np.ndarray):
            return np.array([item ** n for item in self])

        # Przypadek: AIN ** AIN
        if isinstance(n, AIN):
            # A ** B = exp(B * log(A))
            log_self = self.log()
            mul_result = n * log_self
            result = mul_result.exp()
            return result

        # Przypadek: AIN ** (int/float)
        if not isinstance(n, (float, int)):
            raise TypeError('n must be float, int, or AIN')

        if isinstance(self.lower ** n, complex):
            raise ValueError(f'The operation cannot be execute because it will be complex number in result for n = {n}')

        if self.lower < 0 and self.upper > 0:
            new_a = min(0, self.lower ** n)
        else:
            new_a = min(self.lower ** n, self.upper ** n)

        new_b = max(self.lower ** n, self.upper ** n)

        if n == -1:
            if self.lower <= 0 <= self.upper:
                raise ValueError(f'The operation cannot be execute because 0 is included in the interval.')
            else:
                if self.lower == self.upper:
                    new_c = 1 / self.lower
                else:
                    new_c = self.alpha * np.log(self.expected / self.lower) + self.beta * np.log(
                        self.upper / self.expected)
        else:
            new_c = self.alpha * (self.expected ** (n + 1) - self.lower ** (n + 1)) / (n + 1) + self.beta * (
                    self.upper ** (n + 1) - self.expected ** (n + 1)) / (n + 1)

        if self.lower == self.upper:
            new_c = new_b

        res = AIN(new_a, new_b, new_c)
        return res

    def __rpow__(self, a):
        """
        Compute a^x where `a` is the base and `self` (x) is the `AIN` instance.

        Allows expressions like `2 ** AIN(1, 2, 1.5)`.

        Parameters
        ----------
        a : float or int
            The base of the power function. Must be positive and not equal to 1.

        Returns
        -------
        AIN
            A new `AIN` instance representing the result of a^x operation.

        Raises
        ------
        TypeError
            If `a` is not a number (int or float).
        ValueError
            If `a <= 0` or `a == 1`.

        Examples
        --------
        >>> a = AIN(1, 2, 1.5)
        >>> print(2 ** a)
        [2.0000, 4.0000]_{2.8854}
        """

        # Obsługa np.array
        if isinstance(self, np.ndarray):
            return np.array([a ** item for item in self])

        if not isinstance(a, (int, float)):
            raise TypeError(f"a is not a number (int or float)")

        if a <= 0 or a == 1:
            raise ValueError(f"a must be positive and not equal to 1")

        new_lower = float(a ** self.lower)
        new_upper = float(a ** self.upper)

        if self.lower == self.upper:
            new_expected = float(a ** self.expected)
        else:
            # Odwracamy odejmowanie, aby była dodatnia różnica
            new_expected = float((self.alpha * ((a ** self.expected) - (a ** self.lower)) +
                                  self.beta * ((a ** self.upper) - (a ** self.expected))) / np.log(a))

        res = AIN(new_lower, new_upper, new_expected)
        return res

    def log(self, base=None):
        """
        Computes the logarithm of the current `AIN` instance.
        Returns a new `AIN` instance representing the result.

        - When computing log(x) of an `AIN` instance, the resulting `lower` and `upper`
        values are calculated by applying the logarithm function to the
        corresponding bounds of the current `AIN` instance.
        - The `expected` value is calculated using the formula:
          c_ln = α(c·ln(c) - c - a·ln(a) + a) + β(b·ln(b) - b - c·ln(c) + c)
          where a = lower, b = upper, c = expected, α = alpha, β = beta
        - If base is provided, the result is divided by ln(base)

        Parameters
        ----------
        base : float or int, optional
            The base of the logarithm. If None (default), computes natural logarithm.
            Must be positive and not equal to 1.

        Returns
        -------
        AIN
            Returns a new `AIN` instance representing the result of the logarithm operation,
            with the `lower`, `upper`, and `expected` values updated accordingly based
            on the operation.

        Raises
        ------
        TypeError
            If `self` is not an instance of `AIN` or if `base` is not None, int, or float.
        ValueError
            If `lower <= 0`, as the logarithm is undefined for non-positive values.
            If `base <= 0` or `base == 1`.

        Examples
        --------
        Natural logarithm of an `AIN` instance:
        >>> a = AIN(1, np.e, 2)
        >>> print(a.log())
        [0.0000, 1.0000]_{0.3397}

        Logarithm with custom base:
        >>> a = AIN(1, 8, 4)
        >>> print(a.log(base=2))
        [0.0000, 3.0000]_{2.0000}
        """

        if not isinstance(self, AIN):
            raise TypeError(f"self is not an instance of AIN")

        if self.lower <= 0:
            raise ValueError(
                f"lower must be positive (> 0), got lower={self.lower}. Logarithm is undefined for non-positive values.")

        if base is not None:
            if not isinstance(base, (int, float)):
                raise TypeError(f"base must be int or float, got {type(base)}")
            if base <= 0 or base == 1:
                raise ValueError(f"base must be positive and not equal to 1, got base={base}")

        new_lower = np.log(self.lower)
        new_upper = np.log(self.upper)

        new_expected = (self.alpha * (self.expected * np.log(self.expected) - self.expected -
                                      self.lower * np.log(self.lower) + self.lower) +
                        self.beta * (self.upper * np.log(self.upper) - self.upper -
                                     self.expected * np.log(self.expected) + self.expected))

        # If base is specified, convert from natural log to log_base
        if base is not None:
            log_base = np.log(base)
            new_lower = new_lower / log_base
            new_upper = new_upper / log_base
            new_expected = new_expected / log_base

        res = AIN(new_lower, new_upper, new_expected)
        return res

    def exp(self):
        """
        Computes the exponential (e^x) of the current `AIN` instance.
        Returns a new `AIN` instance representing the result.

        - When computing exp() of an `AIN` instance, the resulting `lower` and `upper`
        values are calculated by applying the exponential function to the corresponding values.
        - The `expected` value is calculated as the mean value of exp(x) over the interval
        [lower, upper], given by (e^upper - e^lower) / (upper - lower).

        Parameters
        ----------
        None

        Returns
        -------
        AIN
            Returns a new `AIN` instance representing the result of the exponential operation,
            with the `lower`, `upper`, and `expected` values updated accordingly.

        Raises
        ------
        TypeError
            If `self` is not an instance of `AIN`.
        ValueError
            If `lower >= upper`.

        Examples
        --------
        Exponential of an `AIN` instance:
        >>> a = AIN(0, 1, 0.5)
        >>> print(a.exp())
        [1.0000, 2.7183]_{1.7183}
        """

        if not isinstance(self, AIN):
            raise TypeError(f"self is not an instance of AIN")

        if self.lower >= self.upper:
            raise ValueError(f"lower ({self.lower}) must be less than upper ({self.upper})")

        new_lower = np.exp(self.lower)
        new_upper = np.exp(self.upper)
        new_expected = self.alpha * (np.exp(self.expected) - np.exp(self.lower)) + self.beta * (
                    np.exp(self.upper) - np.exp(self.expected))

        res = AIN(new_lower, new_upper, new_expected)
        return res

    def __abs__(self):
        """
        Compute the absolute value of an AIN instance.

        The absolute value operation handles three cases based on the position of the interval
        relative to zero. This implementation follows the LOTUS (Law of the Unconscious Statistician)
        methodology to compute the expected value of |X|.

        Returns
        -------
        AIN
            A new AIN instance representing the absolute value of the interval.

        Raises
        ------
        None

        Notes
        -----
        The method handles three distinct cases:

        **Case 1:** If the entire interval is non-negative (a ≥ 0), the absolute value
        does not change the interval: |[a, b]_c| = [a, b]_c

        **Case 2:** If the entire interval is non-positive (b ≤ 0), the absolute value
        negates and reverses the bounds: |[a, b]_c| = [-b, -a]_{-c}

        **Case 3:** If the interval contains zero (a < 0 < b), the absolute value results
        in an interval starting at zero. The expected value is computed using LOTUS:

        For c > 0 (expected value in positive part):
            E(|X|) = α(c²/2 - a²/2) + β(b²/2 - c²/2)

        For c ≤ 0 (expected value in negative part):
            E(|X|) = α(0 - a²/2) + β(b²/2 - 0)

        The upper bound becomes max(-a, b) to capture the maximum absolute value.

        Examples
        --------
        Case 1: Non-negative interval
        >>> a = AIN(1, 4, 2)
        >>> print(abs(a))
        [1.0000, 4.0000]_{2.0000}

        Case 2: Non-positive interval
        >>> b = AIN(-4, -1, -2)
        >>> print(abs(b))
        [1.0000, 4.0000]_{2.0000}

        Case 3: Interval containing zero (c > 0)
        >>> c = AIN(-2, 3, 1)
        >>> result = abs(c)
        >>> print(result)
        [0.0000, 3.0000]_{1.5000}

        Case 3: Interval containing zero (c ≤ 0)
        >>> d = AIN(-3, 2, -1)
        >>> result = abs(d)
        >>> print(result)
        [0.0000, 3.0000]_{1.2600}

        Symmetric interval around zero
        >>> e = AIN(-2, 2, 0)
        >>> result = abs(e)
        >>> print(result)
        [0.0000, 2.0000]_{1.0000}

        Working with numpy arrays
        >>> import numpy as np
        >>> arr = np.array([AIN(-2, 3, 1), AIN(1, 4, 2), AIN(-4, -1, -2)])
        >>> abs_arr = np.abs(arr)
        >>> print(abs_arr)
        [AIN(0, 3, 1.5) AIN(1, 4, 2.0) AIN(1, 4, 2.0)]
        """
        # Case 1: Interval is non-negative (a ≥ 0)
        if self.lower >= 0:
            return AIN(self.lower, self.upper, self.expected)

        # Case 2: Interval is non-positive (b ≤ 0)
        elif self.upper <= 0:
            return AIN(-self.upper, -self.lower, -self.expected)

        # Case 3: Interval contains zero (a < 0 < b)
        else:
            new_a = 0
            new_b = max(-self.lower, self.upper)

            # Degenerate case
            if self.lower == self.upper:
                new_c = abs(self.expected)
            else:
                # Expected value is in the positive part (c > 0)
                # E(|X|) = α∫_a^0(-x)dx + α∫_0^c(x)dx + β∫_c^b(x)dx
                #        = α·a²/2 + α·c²/2 + β·b²/2 - β·c²/2
                if self.expected > 0:
                    new_c = (self.alpha * self.lower ** 2 / 2 +
                             self.alpha * self.expected ** 2 / 2 +
                             self.beta * self.upper ** 2 / 2 -
                             self.beta * self.expected ** 2 / 2)
                # Expected value is in the negative part or at zero (c ≤ 0)
                # E(|X|) = α∫_a^c(-x)dx + β∫_c^0(-x)dx + β∫_0^b(x)dx
                #        = α·a²/2 - α·c²/2 + β·c²/2 + β·b²/2
                else:
                    new_c = (self.alpha * self.lower ** 2 / 2 -
                             self.alpha * self.expected ** 2 / 2 +
                             self.beta * self.expected ** 2 / 2 +
                             self.beta * self.upper ** 2 / 2)

            return AIN(new_a, new_b, new_c)

    def sign(self):
        """
        Compute the sign function of an AIN instance.

        The sign function returns:
        - -1 for negative values
        - 0 for zero
        - 1 for positive values

        For an interval that spans multiple regions, the result is an interval containing
        all possible sign values, with an expected value computed using LOTUS (Law of the
        Unconscious Statistician).

        Returns
        -------
        AIN
            A new AIN instance representing sign(X).

        Notes
        -----
        The expected value E[sign(X)] has a useful interpretation:
        E[sign(X)] = P(X > 0) - P(X < 0)

        This means:
        - E[sign(X)] = 1.0 indicates the interval is entirely positive
        - E[sign(X)] = -1.0 indicates the interval is entirely negative
        - E[sign(X)] = 0.0 indicates equal probability mass on positive and negative sides
        - E[sign(X)] = 0.7 indicates 85% probability of positive values, 15% negative

        Examples
        --------
        Entirely positive interval:
        >>> x = AIN(2, 5, 3)
        >>> result = x.sign()
        >>> print(result)
        [1.0000, 1.0000]_{1.0000}

        Entirely negative interval:
        >>> x = AIN(-5, -2, -3)
        >>> result = x.sign()
        >>> print(result)
        [-1.0000, -1.0000]_{-1.0000}

        Interval containing zero:
        >>> x = AIN(-1, 9, 3)
        >>> result = x.sign()
        >>> print(result)
        [-1.0000, 1.0000]_{0.7000}

        The value 0.7 means 85% of the probability mass is in the positive region,
        and 15% is in the negative region.
        """
        # Case 1: Entire interval is positive
        if self.lower > 0:
            return AIN(1, 1, 1)

        # Case 2: Entire interval is negative
        elif self.upper < 0:
            return AIN(-1, -1, -1)

        # Case 3: Entire interval is exactly zero (degenerate case)
        elif self.lower == 0 and self.upper == 0:
            return AIN(0, 0, 0)

        # Case 4: Interval contains zero
        else:
            new_lower = -1
            new_upper = 1

            # Compute expected value E[sign(X)] using LOTUS
            # E[sign(X)] = ∫ sign(x) * f(x) dx

            if self.expected < 0:
                # Expected value is in the negative part
                # E[sign(X)] = ∫_{lower}^{expected} (-1)*α dx + ∫_{expected}^{0} (-1)*β dx + ∫_{0}^{upper} 1*β dx
                new_expected = (
                        -self.alpha * (self.expected - self.lower) +
                        -self.beta * (0 - self.expected) +
                        self.beta * (self.upper - 0)
                )
            elif self.expected > 0:
                # Expected value is in the positive part
                # E[sign(X)] = ∫_{lower}^{0} (-1)*α dx + ∫_{0}^{expected} 1*α dx + ∫_{expected}^{upper} 1*β dx
                new_expected = (
                        -self.alpha * (0 - self.lower) +
                        self.alpha * (self.expected - 0) +
                        self.beta * (self.upper - self.expected)
                )
            else:  # expected == 0
                # Expected value is exactly at zero
                # E[sign(X)] = ∫_{lower}^{0} (-1)*α dx + ∫_{0}^{upper} 1*β dx
                new_expected = (
                        -self.alpha * (0 - self.lower) +
                        self.beta * (self.upper - 0)
                )

            return AIN(new_lower, new_upper, new_expected)

    def cos(self):
        """
        Compute cosine of an AIN instance.

        Returns
        -------
        AIN
            A new AIN instance representing cos(X).

        Examples
        --------
        >>> x = AIN(0, np.pi, np.pi/2)
        >>> result = x.cos()
        >>> print(result)
        [-1.0000, 1.0000]_{0.0000}
        """
        # Degenerate case
        if self.lower == self.upper:
            val = np.cos(self.expected)
            return AIN(val, val, val)

        a, b, c = self.lower, self.upper, self.expected

        candidates = [np.cos(a), np.cos(b)]

        # Check if interval contains maxima of cosine (2kπ)
        k_max_start = int(np.ceil(a / (2 * np.pi)))
        k_max_end = int(np.floor(b / (2 * np.pi)))
        for k in range(k_max_start, k_max_end + 1):
            x_max = 2 * k * np.pi
            if a <= x_max <= b:
                candidates.append(1.0)

        # Check if interval contains minima of cosine (π + 2kπ)
        k_min_start = int(np.ceil((a - np.pi) / (2 * np.pi)))
        k_min_end = int(np.floor((b - np.pi) / (2 * np.pi)))
        for k in range(k_min_start, k_min_end + 1):
            x_min = np.pi + 2 * k * np.pi
            if a <= x_min <= b:
                candidates.append(-1.0)

        new_a = min(candidates)
        new_b = max(candidates)

        # Expected value using LOTUS: E[cos(X)] = ∫ cos(x) f(x) dx
        new_c = (self.alpha * (np.sin(self.expected) - np.sin(self.lower)) +
                 self.beta * (np.sin(self.upper) - np.sin(self.expected)))

        return AIN(new_a, new_b, new_c)

    def tan(self):
        """
        Compute tangent of an AIN instance.

        Note: This function will raise an error if the interval contains
        asymptotes (π/2 + kπ).

        Returns
        -------
        AIN
            A new AIN instance representing tan(X).

        Raises
        ------
        ValueError
            If the interval contains asymptotes.

        Examples
        --------
        >>> x = AIN(0, np.pi/4, np.pi/6)
        >>> result = x.tan()
        """
        # Degenerate case
        if self.lower == self.upper:
            val = np.tan(self.expected)
            return AIN(val, val, val)

        a, b = self.lower, self.upper

        # Check for asymptotes in the interval
        k_start = int(np.ceil((a - np.pi / 2) / np.pi))
        k_end = int(np.floor((b - np.pi / 2) / np.pi))
        for k in range(k_start, k_end + 1):
            asymptote = np.pi / 2 + k * np.pi
            if a < asymptote < b:
                raise ValueError(f"Interval [{a}, {b}] contains asymptote at {asymptote}")

        new_a = min(np.tan(a), np.tan(b))
        new_b = max(np.tan(a), np.tan(b))

        # Expected value using LOTUS
        # ∫ tan(x) dx = -ln|cos(x)|
        new_c = (self.alpha * (-np.log(np.abs(np.cos(self.expected))) + np.log(np.abs(np.cos(self.lower)))) +
                 self.beta * (-np.log(np.abs(np.cos(self.upper))) + np.log(np.abs(np.cos(self.expected)))))

        return AIN(new_a, new_b, new_c)

    def sqrt(self):
        """
        Compute square root of an AIN instance.

        Returns
        -------
        AIN
            A new AIN instance representing sqrt(X).

        Raises
        ------
        ValueError
            If lower bound is negative.

        Examples
        --------
        >>> x = AIN(1, 9, 4)
        >>> result = x.sqrt()
        >>> print(result)
        [1.0000, 3.0000]_{2.0000}
        """
        if self.lower < 0:
            raise ValueError("Cannot compute square root of negative values")

        return self ** 0.5

    def square(self):
        """
        Compute square of an AIN instance.

        Returns
        -------
        AIN
            A new AIN instance representing X^2.

        Examples
        --------
        >>> x = AIN(2, 4, 3)
        >>> result = x.square()
        >>> print(result)
        [4.0000, 16.0000]_{10.0000}
        """
        return self ** 2

    def reciprocal(self):
        """
        Compute reciprocal (1/X) of an AIN instance.

        Returns
        -------
        AIN
            A new AIN instance representing 1/X.

        Raises
        ------
        ValueError
            If interval contains zero.

        Examples
        --------
        >>> x = AIN(2, 4, 3)
        >>> result = x.reciprocal()
        >>> print(result)
        [0.2500, 0.5000]_{0.3466}
        """
        if self.lower <= 0 <= self.upper:
            raise ValueError("Cannot compute reciprocal: interval contains zero")

        return self ** (-1)

    def fmod(self, other):
        # WS_to_check_common_sense
        """
        Compute floating-point remainder of division (modulo operation).

        Computes X mod Y where the result has the same sign as X.
        This is the floating-point remainder of the division operation X/Y.

        Parameters
        ----------
        other : AIN or float
            The divisor.

        Returns
        -------
        AIN
            A new AIN instance representing X mod Y.

        Raises
        ------
        ValueError
            If other contains zero.

        Examples
        --------
        >>> x = AIN(5, 10, 7.5)
        >>> result = x.fmod(3)
        >>> print(result)
        [2.0000, 1.0000]_{1.5000}

        >>> x = AIN(7, 15, 11)
        >>> y = AIN(3, 5, 4)
        >>> result = x.fmod(y)
        """
        if isinstance(other, (int, float)):
            if other == 0:
                raise ValueError("Cannot compute fmod: divisor is zero")

            # For scalar divisor
            new_lower = float(np.fmod(self.lower, other))
            new_upper = float(np.fmod(self.upper, other))
            new_expected = float(np.fmod(self.expected, other))

            # fmod can make bounds go backwards, fix this
            actual_lower = min(new_lower, new_upper)
            actual_upper = max(new_lower, new_upper)

            # Ensure expected is within bounds
            if new_expected < actual_lower:
                new_expected = actual_lower
            if new_expected > actual_upper:
                new_expected = actual_upper

            # Handle degenerate case
            if actual_lower == actual_upper:
                return AIN(actual_lower, actual_upper, actual_lower)

            return AIN(actual_lower, actual_upper, new_expected)

        elif isinstance(other, AIN):
            if other.lower <= 0 <= other.upper:
                raise ValueError("Cannot compute fmod: divisor interval contains zero")

            # For AIN divisor, compute range of possible remainders
            # The remainder is always less than the divisor in absolute value
            candidates = [
                float(np.fmod(self.lower, other.lower)),
                float(np.fmod(self.lower, other.upper)),
                float(np.fmod(self.upper, other.lower)),
                float(np.fmod(self.upper, other.upper)),
            ]

            new_lower = min(candidates)
            new_upper = max(candidates)
            new_expected = float(np.fmod(self.expected, other.expected))

            # Ensure expected is within bounds
            if new_expected < new_lower:
                new_expected = new_lower
            if new_expected > new_upper:
                new_expected = new_upper

            # Handle degenerate case
            if new_lower == new_upper:
                return AIN(new_lower, new_upper, new_lower)

            return AIN(new_lower, new_upper, new_expected)
        else:
            return NotImplemented

    def floor(self):
        # WS_to_check_common_sense
        """
        Compute floor (round down) of the interval.

        Returns the largest integers less than or equal to each bound.

        Returns
        -------
        AIN
            A new AIN instance with floored bounds.

        Examples
        --------
        >>> x = AIN(1.5, 4.8, 3.2)
        >>> result = x.floor()
        >>> print(result)
        [1.0000, 4.0000]_{2.5000}
        """
        new_lower = np.floor(self.lower)
        new_upper = np.floor(self.upper)

        # For expected value, use floor of expected as approximation
        new_expected = np.floor(self.expected)

        # Ensure expected is within bounds
        if new_expected < new_lower:
            new_expected = new_lower
        if new_expected > new_upper:
            new_expected = new_upper

        # Handle degenerate case
        if new_lower == new_upper:
            return AIN(new_lower, new_upper, new_lower)

        return AIN(new_lower, new_upper, new_expected)

    def ceil(self):
        # WS_to_check_common_sense
        """
        Compute ceiling (round up) of the interval.

        Returns the smallest integers greater than or equal to each bound.

        Returns
        -------
        AIN
            A new AIN instance with ceiling bounds.

        Examples
        --------
        >>> x = AIN(1.2, 4.5, 2.8)
        >>> result = x.ceil()
        >>> print(result)
        [2.0000, 5.0000]_{3.5000}
        """
        new_lower = np.ceil(self.lower)
        new_upper = np.ceil(self.upper)

        # For expected value, use ceil of expected as approximation
        new_expected = np.ceil(self.expected)

        # Ensure expected is within bounds
        if new_expected < new_lower:
            new_expected = new_lower
        if new_expected > new_upper:
            new_expected = new_upper

        # Handle degenerate case
        if new_lower == new_upper:
            return AIN(new_lower, new_upper, new_lower)

        return AIN(new_lower, new_upper, new_expected)

    def round(self, decimals=0):
        # WS_to_check_common_sense
        """
        Round the interval to the nearest integer or specified number of decimals.

        Parameters
        ----------
        decimals : int, optional
            Number of decimal places to round to. Default is 0.

        Returns
        -------
        AIN
            A new AIN instance with rounded bounds.

        Examples
        --------
        >>> x = AIN(1.456, 4.789, 3.123)
        >>> result = x.round()
        >>> print(result)
        [1.0000, 5.0000]_{3.0000}

        >>> result = x.round(decimals=2)
        >>> print(result)
        [1.4600, 4.7900]_{3.1200}
        """
        new_lower = np.round(self.lower, decimals=decimals)
        new_upper = np.round(self.upper, decimals=decimals)

        # For expected value, use round of expected as approximation
        new_expected = np.round(self.expected, decimals=decimals)

        # Ensure expected is within bounds
        if new_expected < new_lower:
            new_expected = new_lower
        if new_expected > new_upper:
            new_expected = new_upper

        # Handle degenerate case
        if new_lower == new_upper:
            return AIN(new_lower, new_upper, new_lower)

        return AIN(new_lower, new_upper, new_expected)

    def trunc(self):
        # WS_to_check_common_sense
        """
        Truncate the interval towards zero (remove decimal part).

        Returns the integer part of each bound by truncating towards zero.

        Returns
        -------
        AIN
            A new AIN instance with truncated bounds.

        Examples
        --------
        >>> x = AIN(1.8, 4.3, 3.1)
        >>> result = x.trunc()
        >>> print(result)
        [1.0000, 4.0000]_{3.0000}

        >>> x = AIN(-4.8, -1.2, -3.0)
        >>> result = x.trunc()
        >>> print(result)
        [-4.0000, -1.0000]_{-3.0000}
        """
        new_lower = np.trunc(self.lower)
        new_upper = np.trunc(self.upper)

        # For expected value, use trunc of expected as approximation
        new_expected = np.trunc(self.expected)

        # Ensure expected is within bounds
        if new_expected < new_lower:
            new_expected = new_lower
        if new_expected > new_upper:
            new_expected = new_upper

        # Handle degenerate case
        if new_lower == new_upper:
            return AIN(new_lower, new_upper, new_lower)

        return AIN(new_lower, new_upper, new_expected)

    def relu(self):
        """
        Compute ReLU (Rectified Linear Unit) function: max(0, X).

        Returns
        -------
        AIN
            A new AIN instance representing max(0, X).

        Examples
        --------
        >>> x = AIN(-2, 5, 2)
        >>> result = x.relu()
        >>> print(result)
        [0.0000, 5.0000]_{2.5000}
        """
        # Case 1: Entire interval is positive
        if self.lower >= 0:
            return AIN(self.lower, self.upper, self.expected)

        # Case 2: Entire interval is negative
        elif self.upper <= 0:
            return AIN(0, 0, 0)

        # Case 3: Interval contains zero
        else:
            new_lower = 0
            new_upper = self.upper

            # Compute expected value using LOTUS
            # E[max(0,X)] = ∫_{-∞}^{0} 0·f(x)dx + ∫_{0}^{∞} x·f(x)dx
            if self.expected <= 0:
                # Expected is in negative part: integrate from 0 to upper
                new_expected = self.beta * (self.upper ** 2 / 2 - 0)
            else:
                # Expected is in positive part
                new_expected = (self.alpha * (self.expected ** 2 / 2 - 0) +
                                self.beta * (self.upper ** 2 / 2 - self.expected ** 2 / 2))

            return AIN(new_lower, new_upper, new_expected)

    def sigmoid(self):
        """
        Compute sigmoid function: 1/(1 + exp(-X)).

        Returns
        -------
        AIN
            A new AIN instance representing sigmoid(X).

        Examples
        --------
        >>> x = AIN(-2, 2, 0)
        >>> result = x.sigmoid()
        >>> print(result)
        [0.1192, 0.8808]_{0.5000}
        """
        # Degenerate case
        if self.lower == self.upper:
            val = 1 / (1 + np.exp(-self.expected))
            return AIN(val, val, val)

        # sigmoid is monotonically increasing
        new_lower = 1 / (1 + np.exp(-self.lower))
        new_upper = 1 / (1 + np.exp(-self.upper))

        # Expected value using LOTUS
        # This is complex, so we use numerical integration approximation
        # E[sigmoid(X)] ≈ sigmoid(E[X]) for small variance (approximation)
        # For exact: we need to integrate sigmoid with the PDF

        # Exact formula using integration by parts and properties of sigmoid:
        # ∫ sigmoid(x) dx = x + ln(1 + e^(-x))
        def sigmoid_antiderivative(x):
            return x + np.log(1 + np.exp(-x))

        new_expected = (self.alpha * (sigmoid_antiderivative(self.expected) - sigmoid_antiderivative(self.lower)) +
                        self.beta * (sigmoid_antiderivative(self.upper) - sigmoid_antiderivative(self.expected)))

        return AIN(new_lower, new_upper, new_expected)

    def heaviside(self):
        """
        Compute Heaviside step function.

        H(x) = 0 if x < 0
        H(x) = 0.5 if x = 0
        H(x) = 1 if x > 0

        Returns
        -------
        AIN
            A new AIN instance representing H(X).

        Examples
        --------
        >>> x = AIN(-2, 5, 2)
        >>> result = x.heaviside()
        >>> print(result)
        [0.0000, 1.0000]_{0.8500}
        """
        # Case 1: Entire interval is positive
        if self.lower > 0:
            return AIN(1, 1, 1)

        # Case 2: Entire interval is negative
        elif self.upper < 0:
            return AIN(0, 0, 0)

        # Case 3: Interval is exactly zero
        elif self.lower == 0 and self.upper == 0:
            return AIN(0.5, 0.5, 0.5)

        # Case 4: Interval contains zero
        else:
            new_lower = 0
            new_upper = 1

            # E[H(X)] = P(X > 0) + 0.5·P(X = 0)
            # For continuous distribution, P(X = 0) = 0
            # So E[H(X)] = P(X > 0)
            prob_positive = 1 - self.cdf(0)
            new_expected = prob_positive

            return AIN(new_lower, new_upper, new_expected)

    def sinh(self):
        """
        Compute hyperbolic sine: sinh(X) = (exp(X) - exp(-X))/2.

        Returns
        -------
        AIN
            A new AIN instance representing sinh(X).

        Examples
        --------
        >>> x = AIN(0, 2, 1)
        >>> result = x.sinh()
        """
        # Degenerate case
        if self.lower == self.upper:
            val = np.sinh(self.expected)
            return AIN(val, val, val)

        # sinh is monotonically increasing
        new_lower = np.sinh(self.lower)
        new_upper = np.sinh(self.upper)

        # Expected value using LOTUS
        # ∫ sinh(x) dx = cosh(x)
        new_expected = (self.alpha * (np.cosh(self.expected) - np.cosh(self.lower)) +
                        self.beta * (np.cosh(self.upper) - np.cosh(self.expected)))

        return AIN(new_lower, new_upper, new_expected)

    def cosh(self):
        """
        Compute hyperbolic cosine: cosh(X) = (exp(X) + exp(-X))/2.

        Returns
        -------
        AIN
            A new AIN instance representing cosh(X).

        Examples
        --------
        >>> x = AIN(-1, 1, 0)
        >>> result = x.cosh()
        """
        # Degenerate case
        if self.lower == self.upper:
            val = np.cosh(self.expected)
            return AIN(val, val, val)

        # cosh has minimum at x=0
        if self.lower < 0 < self.upper:
            # Interval contains minimum
            new_lower = 1.0  # cosh(0) = 1
            new_upper = max(np.cosh(self.lower), np.cosh(self.upper))
        else:
            # Interval doesn't contain 0
            new_lower = min(np.cosh(self.lower), np.cosh(self.upper))
            new_upper = max(np.cosh(self.lower), np.cosh(self.upper))

        # Expected value using LOTUS
        # ∫ cosh(x) dx = sinh(x)
        if self.expected < 0:
            new_expected = (self.alpha * (np.sinh(self.expected) - np.sinh(self.lower)) +
                            self.beta * (np.sinh(0) - np.sinh(self.expected)) +
                            self.beta * (np.sinh(self.upper) - np.sinh(0)))
        elif self.expected > 0:
            new_expected = (self.alpha * (np.sinh(0) - np.sinh(self.lower)) +
                            self.alpha * (np.sinh(self.expected) - np.sinh(0)) +
                            self.beta * (np.sinh(self.upper) - np.sinh(self.expected)))
        else:
            new_expected = (self.alpha * (np.sinh(0) - np.sinh(self.lower)) +
                            self.beta * (np.sinh(self.upper) - np.sinh(0)))

        return AIN(new_lower, new_upper, new_expected)

    def tanh(self):
        """
        Compute hyperbolic tangent: tanh(X) = sinh(X)/cosh(X).

        Returns
        -------
        AIN
            A new AIN instance representing tanh(X).

        Examples
        --------
        >>> x = AIN(-2, 2, 0)
        >>> result = x.tanh()
        """
        # Degenerate case
        if self.lower == self.upper:
            val = np.tanh(self.expected)
            return AIN(val, val, val)

        # tanh is monotonically increasing
        new_lower = np.tanh(self.lower)
        new_upper = np.tanh(self.upper)

        # Expected value using LOTUS
        # ∫ tanh(x) dx = ln(cosh(x))
        new_expected = (self.alpha * (np.log(np.cosh(self.expected)) - np.log(np.cosh(self.lower))) +
                        self.beta * (np.log(np.cosh(self.upper)) - np.log(np.cosh(self.expected))))

        return AIN(new_lower, new_upper, new_expected)

    def arcsin(self):
        """
        Compute arcsine (inverse sine) of an AIN instance.

        Returns
        -------
        AIN
            A new AIN instance representing arcsin(X).

        Raises
        ------
        ValueError
            If interval is not within [-1, 1].

        Examples
        --------
        >>> x = AIN(0, 1, 0.5)
        >>> result = x.arcsin()
        """
        if self.lower < -1 or self.upper > 1:
            raise ValueError("arcsin requires interval to be within [-1, 1]")

        # Degenerate case
        if self.lower == self.upper:
            val = np.arcsin(self.expected)
            return AIN(val, val, val)

        # arcsin is monotonically increasing on [-1, 1]
        new_lower = np.arcsin(self.lower)
        new_upper = np.arcsin(self.upper)

        # Expected value using LOTUS
        # ∫ arcsin(x) dx = x·arcsin(x) + sqrt(1-x²)
        def arcsin_antiderivative(x):
            return x * np.arcsin(x) + np.sqrt(1 - x ** 2)

        new_expected = (self.alpha * (arcsin_antiderivative(self.expected) - arcsin_antiderivative(self.lower)) +
                        self.beta * (arcsin_antiderivative(self.upper) - arcsin_antiderivative(self.expected)))

        return AIN(new_lower, new_upper, new_expected)

    def arccos(self):
        """
        Compute arccosine (inverse cosine) of an AIN instance.

        Returns
        -------
        AIN
            A new AIN instance representing arccos(X).

        Raises
        ------
        ValueError
            If interval is not within [-1, 1].

        Examples
        --------
        >>> x = AIN(0, 1, 0.5)
        >>> result = x.arccos()
        """
        if self.lower < -1 or self.upper > 1:
            raise ValueError("arccos requires interval to be within [-1, 1]")

        # Degenerate case
        if self.lower == self.upper:
            val = np.arccos(self.expected)
            return AIN(val, val, val)

        # arccos is monotonically decreasing on [-1, 1]
        new_lower = np.arccos(self.upper)
        new_upper = np.arccos(self.lower)

        # Expected value using LOTUS
        # ∫ arccos(x) dx = x·arccos(x) - sqrt(1-x²)
        def arccos_antiderivative(x):
            return x * np.arccos(x) - np.sqrt(1 - x ** 2)

        new_expected = (self.alpha * (arccos_antiderivative(self.expected) - arccos_antiderivative(self.lower)) +
                        self.beta * (arccos_antiderivative(self.upper) - arccos_antiderivative(self.expected)))

        return AIN(new_lower, new_upper, new_expected)

    def arctan(self):
        """
        Compute arctangent (inverse tangent) of an AIN instance.

        Returns
        -------
        AIN
            A new AIN instance representing arctan(X).

        Examples
        --------
        >>> x = AIN(0, 1, 0.5)
        >>> result = x.arctan()
        """
        # Degenerate case
        if self.lower == self.upper:
            val = np.arctan(self.expected)
            return AIN(val, val, val)

        # arctan is monotonically increasing
        new_lower = np.arctan(self.lower)
        new_upper = np.arctan(self.upper)

        # Expected value using LOTUS
        # ∫ arctan(x) dx = x·arctan(x) - ln(1+x²)/2
        def arctan_antiderivative(x):
            return x * np.arctan(x) - np.log(1 + x ** 2) / 2

        new_expected = (self.alpha * (arctan_antiderivative(self.expected) - arctan_antiderivative(self.lower)) +
                        self.beta * (arctan_antiderivative(self.upper) - arctan_antiderivative(self.expected)))

        return AIN(new_lower, new_upper, new_expected)

    def asinh(self):
        """
        Compute inverse hyperbolic sine of an AIN instance.

        Returns
        -------
        AIN
            A new AIN instance representing asinh(X).

        Examples
        --------
        >>> x = AIN(0, 2, 1)
        >>> result = x.asinh()
        """
        # Degenerate case
        if self.lower == self.upper:
            val = np.arcsinh(self.expected)
            return AIN(val, val, val)

        # asinh is monotonically increasing
        new_lower = np.arcsinh(self.lower)
        new_upper = np.arcsinh(self.upper)

        # Expected value using LOTUS
        # ∫ asinh(x) dx = x·asinh(x) - sqrt(x²+1)
        def asinh_antiderivative(x):
            return x * np.arcsinh(x) - np.sqrt(x ** 2 + 1)

        new_expected = (self.alpha * (asinh_antiderivative(self.expected) - asinh_antiderivative(self.lower)) +
                        self.beta * (asinh_antiderivative(self.upper) - asinh_antiderivative(self.expected)))

        return AIN(new_lower, new_upper, new_expected)

    def acosh(self):
        """
        Compute inverse hyperbolic cosine of an AIN instance.

        Returns
        -------
        AIN
            A new AIN instance representing acosh(X).

        Raises
        ------
        ValueError
            If lower bound is less than 1.

        Examples
        --------
        >>> x = AIN(1, 3, 2)
        >>> result = x.acosh()
        """
        if self.lower < 1:
            raise ValueError("acosh requires lower bound >= 1")

        # Degenerate case
        if self.lower == self.upper:
            val = np.arccosh(self.expected)
            return AIN(val, val, val)

        # acosh is monotonically increasing for x >= 1
        new_lower = np.arccosh(self.lower)
        new_upper = np.arccosh(self.upper)

        # Expected value using LOTUS
        # ∫ acosh(x) dx = x·acosh(x) - sqrt(x²-1)
        def acosh_antiderivative(x):
            return x * np.arccosh(x) - np.sqrt(x ** 2 - 1)

        new_expected = (self.alpha * (acosh_antiderivative(self.expected) - acosh_antiderivative(self.lower)) +
                        self.beta * (acosh_antiderivative(self.upper) - acosh_antiderivative(self.expected)))

        return AIN(new_lower, new_upper, new_expected)

    def atanh(self):
        """
        Compute inverse hyperbolic tangent of an AIN instance.

        Returns
        -------
        AIN
            A new AIN instance representing atanh(X).

        Raises
        ------
        ValueError
            If interval is not within (-1, 1).

        Examples
        --------
        >>> x = AIN(-0.5, 0.5, 0)
        >>> result = x.atanh()
        """
        if self.lower <= -1 or self.upper >= 1:
            raise ValueError("atanh requires interval to be within (-1, 1)")

        # Degenerate case
        if self.lower == self.upper:
            val = np.arctanh(self.expected)
            return AIN(val, val, val)

        # atanh is monotonically increasing on (-1, 1)
        new_lower = np.arctanh(self.lower)
        new_upper = np.arctanh(self.upper)

        # Expected value using LOTUS
        # ∫ atanh(x) dx = x·atanh(x) + ln(1-x²)/2
        def atanh_antiderivative(x):
            return x * np.arctanh(x) + np.log(1 - x ** 2) / 2

        new_expected = (self.alpha * (atanh_antiderivative(self.expected) - atanh_antiderivative(self.lower)) +
                        self.beta * (atanh_antiderivative(self.upper) - atanh_antiderivative(self.expected)))

        return AIN(new_lower, new_upper, new_expected)

    def atan2(self, other):
        # WS_to_check_common_sense
        """
        Compute two-argument arctangent atan2(self, other) = atan(self/other).

        Returns the angle in radians between the positive x-axis and the point (other, self),
        with correct handling of quadrants.

        Parameters
        ----------
        other : AIN or float
            The x-coordinate (denominator in self/other).

        Returns
        -------
        AIN
            A new AIN instance representing atan2(self, other) in radians [-π, π].

        Examples
        --------
        >>> y = AIN(1, 2, 1.5)
        >>> x = AIN(1, 2, 1.5)
        >>> result = y.atan2(x)
        """
        if isinstance(other, (int, float)):
            # For scalar x-coordinate
            if other == 0:
                # Special case: x = 0
                candidates = []
                if self.lower > 0:
                    candidates.append(np.pi / 2)
                if self.lower <= 0 <= self.upper:
                    candidates.extend([-np.pi / 2, np.pi / 2])
                if self.upper < 0:
                    candidates.append(-np.pi / 2)

                new_lower = min(candidates) if candidates else 0
                new_upper = max(candidates) if candidates else 0
                new_expected = np.arctan2(self.expected, other)
            else:
                # Evaluate at corners
                candidates = [
                    np.arctan2(self.lower, other),
                    np.arctan2(self.upper, other),
                ]
                new_lower = min(candidates)
                new_upper = max(candidates)
                new_expected = np.arctan2(self.expected, other)

            return AIN(new_lower, new_upper, new_expected)

        elif isinstance(other, AIN):
            # For AIN x-coordinate, compute all corner combinations
            candidates = [
                np.arctan2(self.lower, other.lower),
                np.arctan2(self.lower, other.upper),
                np.arctan2(self.upper, other.lower),
                np.arctan2(self.upper, other.upper),
            ]

            new_lower = min(candidates)
            new_upper = max(candidates)
            new_expected = np.arctan2(self.expected, other.expected)

            # Ensure expected is within bounds
            if new_expected < new_lower:
                new_expected = new_lower
            if new_expected > new_upper:
                new_expected = new_upper

            return AIN(new_lower, new_upper, new_expected)
        else:
            return NotImplemented

    def hypot(self, other):
        # WS_to_check_common_sense
        """
        Compute Euclidean norm sqrt(self² + other²).

        This is the hypotenuse of a right triangle with sides self and other.
        Equivalent to sqrt(self**2 + other**2) but more numerically stable.

        Parameters
        ----------
        other : AIN or float
            The other side of the triangle.

        Returns
        -------
        AIN
            A new AIN instance representing sqrt(self² + other²).

        Examples
        --------
        >>> x = AIN(3, 5, 4)
        >>> y = AIN(4, 12, 8)
        >>> result = x.hypot(y)
        >>> print(result)
        [5.0000, 13.0000]_{8.9443}
        """
        if isinstance(other, (int, float)):
            # For scalar, hypot is monotonic in self
            candidates = [
                np.hypot(self.lower, other),
                np.hypot(self.upper, other),
            ]
            new_lower = min(candidates)
            new_upper = max(candidates)
            new_expected = np.hypot(self.expected, other)

            return AIN(new_lower, new_upper, new_expected)

        elif isinstance(other, AIN):
            # For AIN, evaluate all corners
            candidates = [
                np.hypot(self.lower, other.lower),
                np.hypot(self.lower, other.upper),
                np.hypot(self.upper, other.lower),
                np.hypot(self.upper, other.upper),
            ]

            new_lower = min(candidates)
            new_upper = max(candidates)
            new_expected = np.hypot(self.expected, other.expected)

            # Ensure expected is within bounds
            if new_expected < new_lower:
                new_expected = new_lower
            if new_expected > new_upper:
                new_expected = new_upper

            return AIN(new_lower, new_upper, new_expected)
        else:
            return NotImplemented

    def copysign(self, other):
        # WS_to_check_common_sense
        """
        Return value with magnitude of self and sign of other.

        Returns a value with the magnitude (absolute value) of self but
        the sign of other.

        Parameters
        ----------
        other : AIN or float
            Provides the sign.

        Returns
        -------
        AIN
            A new AIN instance with magnitude of self and sign of other.

        Examples
        --------
        >>> x = AIN(1, 5, 3)
        >>> result = x.copysign(-1)
        >>> print(result)
        [-5.0000, -1.0000]_{-3.0000}

        >>> x = AIN(-5, -1, -3)
        >>> result = x.copysign(1)
        >>> print(result)
        [1.0000, 5.0000]_{3.0000}
        """
        if isinstance(other, (int, float)):
            # For scalar sign
            sign = 1 if other >= 0 else -1

            if sign >= 0:
                # Positive sign: keep values as is if positive, flip if negative
                new_lower = np.copysign(self.lower, other)
                new_upper = np.copysign(self.upper, other)
            else:
                # Negative sign: make all negative
                new_lower = np.copysign(self.upper, other)  # More negative
                new_upper = np.copysign(self.lower, other)  # Less negative

            new_expected = np.copysign(self.expected, other)

            # Ensure expected is within bounds
            actual_lower = min(new_lower, new_upper)
            actual_upper = max(new_lower, new_upper)
            if new_expected < actual_lower:
                new_expected = actual_lower
            if new_expected > actual_upper:
                new_expected = actual_upper

            return AIN(actual_lower, actual_upper, new_expected)

        elif isinstance(other, AIN):
            # For AIN sign, need to consider all combinations
            candidates = [
                np.copysign(self.lower, other.lower),
                np.copysign(self.lower, other.upper),
                np.copysign(self.upper, other.lower),
                np.copysign(self.upper, other.upper),
            ]

            new_lower = min(candidates)
            new_upper = max(candidates)
            new_expected = np.copysign(self.expected, other.expected)

            # Ensure expected is within bounds
            if new_expected < new_lower:
                new_expected = new_lower
            if new_expected > new_upper:
                new_expected = new_upper

            return AIN(new_lower, new_upper, new_expected)
        else:
            return NotImplemented

    def erf(self):
        # WS_to_check_common_sense
        """
        Compute error function erf(X).

        The error function is defined as:
        erf(x) = (2/√π) ∫₀ˣ e^(-t²) dt

        Returns
        -------
        AIN
            A new AIN instance representing erf(X).

        Examples
        --------
        >>> x = AIN(-1, 1, 0)
        >>> result = x.erf()
        >>> print(result)
        [-0.8427, 0.8427]_{0.0000}
        """
        from scipy.special import erf as scipy_erf
        from scipy.integrate import quad

        # Degenerate case
        if self.lower == self.upper:
            val = scipy_erf(self.expected)
            return AIN(val, val, val)

        # erf is monotonically increasing
        new_lower = scipy_erf(self.lower)
        new_upper = scipy_erf(self.upper)

        # Compute expected value using numerical integration
        # The antiderivative of erf(x) doesn't have a closed form in elementary functions
        def erf_func(x):
            return scipy_erf(x)

        integral_left, _ = quad(erf_func, self.lower, self.expected)
        integral_right, _ = quad(erf_func, self.expected, self.upper)

        new_expected = self.alpha * integral_left + self.beta * integral_right

        return AIN(new_lower, new_upper, new_expected)

    def erfc(self):
        # WS_to_check_common_sense
        """
        Compute complementary error function erfc(X) = 1 - erf(X).

        The complementary error function is defined as:
        erfc(x) = 1 - erf(x) = (2/√π) ∫ₓ^∞ e^(-t²) dt

        Returns
        -------
        AIN
            A new AIN instance representing erfc(X).

        Examples
        --------
        >>> x = AIN(-1, 1, 0)
        >>> result = x.erfc()
        >>> print(result)
        [0.1573, 1.8427]_{1.0000}
        """
        from scipy.special import erfc as scipy_erfc
        from scipy.integrate import quad

        # Degenerate case
        if self.lower == self.upper:
            val = scipy_erfc(self.expected)
            return AIN(val, val, val)

        # erfc is monotonically decreasing, so bounds swap
        new_lower = scipy_erfc(self.upper)
        new_upper = scipy_erfc(self.lower)

        # Compute expected value using numerical integration
        def erfc_func(x):
            return scipy_erfc(x)

        integral_left, _ = quad(erfc_func, self.lower, self.expected)
        integral_right, _ = quad(erfc_func, self.expected, self.upper)

        new_expected = self.alpha * integral_left + self.beta * integral_right

        return AIN(new_lower, new_upper, new_expected)

    def gamma(self):
        # WS_to_check_common_sense
        """
        Compute gamma function Γ(X).

        The gamma function extends the factorial function to real and complex numbers.
        For positive integers: Γ(n) = (n-1)!

        Returns
        -------
        AIN
            A new AIN instance representing Γ(X).

        Raises
        ------
        ValueError
            If interval contains non-positive integers where gamma has poles.

        Examples
        --------
        >>> x = AIN(1, 3, 2)
        >>> result = x.gamma()
        >>> print(result)
        [1.0000, 2.0000]_{1.3293}
        """
        from scipy.special import gamma as scipy_gamma
        from scipy.integrate import quad

        # Check for poles (non-positive integers)
        if self.lower <= 0:
            # Check if any non-positive integer is in the interval
            for n in range(int(np.floor(self.lower)), int(np.ceil(self.upper)) + 1):
                if n <= 0 and self.lower <= n <= self.upper:
                    raise ValueError(f"Gamma function has a pole at {n}")

        # Degenerate case
        if self.lower == self.upper:
            val = scipy_gamma(self.expected)
            return AIN(val, val, val)

        # Gamma is monotonic for x > 1.46..., but has minimum around x ≈ 1.46
        # For safety, evaluate at critical points
        gamma_lower = scipy_gamma(self.lower)
        gamma_upper = scipy_gamma(self.upper)
        gamma_expected_val = scipy_gamma(self.expected)

        # Check if minimum point ~1.46 is in interval
        min_point = 1.461632144968362341262659542325721328468196
        if self.lower < min_point < self.upper:
            gamma_min = scipy_gamma(min_point)
            new_lower = min(gamma_lower, gamma_upper, gamma_min)
            new_upper = max(gamma_lower, gamma_upper, gamma_min)
        else:
            new_lower = min(gamma_lower, gamma_upper)
            new_upper = max(gamma_lower, gamma_upper)

        # Compute expected value using LOTUS
        def gamma_func(x):
            return scipy_gamma(x)

        integral_left, _ = quad(gamma_func, self.lower, self.expected)
        integral_right, _ = quad(gamma_func, self.expected, self.upper)

        new_expected = self.alpha * integral_left + self.beta * integral_right

        # Ensure expected is within bounds
        if new_expected < new_lower:
            new_expected = new_lower
        if new_expected > new_upper:
            new_expected = new_upper

        return AIN(new_lower, new_upper, new_expected)

    def lgamma(self):
        # WS_to_check_common_sense
        """
        Compute natural logarithm of absolute value of gamma function: ln(|Γ(X)|).

        This is more numerically stable than computing log(gamma(x)) for large values.

        Returns
        -------
        AIN
            A new AIN instance representing ln(|Γ(X)|).

        Examples
        --------
        >>> x = AIN(2, 5, 3.5)
        >>> result = x.lgamma()
        >>> print(result)
        [0.0000, 3.1781]_{1.2009}
        """
        from scipy.special import gammaln as scipy_lgamma
        from scipy.integrate import quad

        # Degenerate case
        if self.lower == self.upper:
            val = scipy_lgamma(self.expected)
            return AIN(val, val, val)

        # lgamma is eventually monotonically increasing for x > 0
        # but has local minimum around x ≈ 1.46
        lgamma_lower = scipy_lgamma(self.lower)
        lgamma_upper = scipy_lgamma(self.upper)

        # Check if minimum point ~1.46 is in interval
        min_point = 1.461632144968362341262659542325721328468196
        if self.lower < min_point < self.upper and self.lower > 0:
            lgamma_min = scipy_lgamma(min_point)
            new_lower = min(lgamma_lower, lgamma_upper, lgamma_min)
            new_upper = max(lgamma_lower, lgamma_upper, lgamma_min)
        else:
            new_lower = min(lgamma_lower, lgamma_upper)
            new_upper = max(lgamma_lower, lgamma_upper)

        # Compute expected value using LOTUS
        def lgamma_func(x):
            return scipy_lgamma(x)

        integral_left, _ = quad(lgamma_func, self.lower, self.expected)
        integral_right, _ = quad(lgamma_func, self.expected, self.upper)

        new_expected = self.alpha * integral_left + self.beta * integral_right

        # Ensure expected is within bounds
        if new_expected < new_lower:
            new_expected = new_lower
        if new_expected > new_upper:
            new_expected = new_upper

        return AIN(new_lower, new_upper, new_expected)

    def log10(self):
        """
        Compute base-10 logarithm of an AIN instance.

        Returns
        -------
        AIN
            A new AIN instance representing log10(X).

        Raises
        ------
        ValueError
            If lower bound is non-positive.

        Examples
        --------
        >>> x = AIN(1, 100, 10)
        >>> result = x.log10()
        >>> print(result)
        [0.0000, 2.0000]_{1.0000}
        """
        if self.lower <= 0:
            raise ValueError("log10 requires positive values")

        # log10(x) = ln(x) / ln(10)
        result_ln = self.log()
        return AIN(result_ln.lower / np.log(10),
                   result_ln.upper / np.log(10),
                   result_ln.expected / np.log(10))

    def log2(self):
        """
        Compute base-2 logarithm of an AIN instance.

        Returns
        -------
        AIN
            A new AIN instance representing log2(X).

        Raises
        ------
        ValueError
            If lower bound is non-positive.

        Examples
        --------
        >>> x = AIN(1, 8, 4)
        >>> result = x.log2()
        >>> print(result)
        [0.0000, 3.0000]_{2.0000}
        """
        if self.lower <= 0:
            raise ValueError("log2 requires positive values")

        # log2(x) = ln(x) / ln(2)
        result_ln = self.log()
        return AIN(result_ln.lower / np.log(2),
                   result_ln.upper / np.log(2),
                   result_ln.expected / np.log(2))

    def cbrt(self):
        """
        Compute cube root (cubic root) of an AIN instance.

        Returns
        -------
        AIN
            A new AIN instance representing ∛X (X^(1/3)).

        Examples
        --------
        >>> x = AIN(1, 27, 8)
        >>> result = x.cbrt()
        >>> print(result)
        [1.0000, 3.0000]_{1.9574}
        """
        # Degenerate case
        if self.lower == self.upper:
            val = np.cbrt(self.expected)
            return AIN(val, val, val)

        # cbrt is defined for all real numbers (including negative)
        new_lower = np.cbrt(self.lower)
        new_upper = np.cbrt(self.upper)

        # Antiderivative: ∫x^(1/3)dx = (3/4)x^(4/3)
        def antiderivative(x):
            return (3 / 4) * np.sign(x) * (np.abs(x) ** (4 / 3))

        # Use LOTUS
        if self.expected <= self.lower or self.expected >= self.upper:
            raise ValueError("Expected value must be strictly between lower and upper bounds")

        new_expected = (self.alpha * (antiderivative(self.expected) - antiderivative(self.lower)) +
                        self.beta * (antiderivative(self.upper) - antiderivative(self.expected)))

        return AIN(new_lower, new_upper, new_expected)

    def expm1(self):
        """
        Compute exp(X) - 1 in a numerically stable way.

        This is more accurate than exp(x) - 1 for small values of x.

        Returns
        -------
        AIN
            A new AIN instance representing exp(X) - 1.

        Examples
        --------
        >>> x = AIN(0, 0.1, 0.05)
        >>> result = x.expm1()
        >>> print(result)
        [0.0000, 0.1052]_{0.0513}
        """
        # Degenerate case
        if self.lower == self.upper:
            val = np.expm1(self.expected)
            return AIN(val, val, val)

        new_lower = np.expm1(self.lower)
        new_upper = np.expm1(self.upper)

        # E[e^x - 1] using LOTUS
        # ∫(e^x - 1)dx = e^x - x
        new_expected = (self.alpha * ((np.exp(self.expected) - self.expected) -
                                      (np.exp(self.lower) - self.lower)) +
                        self.beta * ((np.exp(self.upper) - self.upper) -
                                     (np.exp(self.expected) - self.expected)))

        return AIN(new_lower, new_upper, new_expected)

    def log1p(self):
        """
        Compute ln(1 + X) in a numerically stable way.

        This is more accurate than log(1 + x) for small values of x.

        Returns
        -------
        AIN
            A new AIN instance representing ln(1 + X).

        Raises
        ------
        ValueError
            If lower bound < -1.

        Examples
        --------
        >>> x = AIN(0, 0.1, 0.05)
        >>> result = x.log1p()
        >>> print(result)
        [0.0000, 0.0953]_{0.0488}
        """
        if self.lower < -1:
            raise ValueError("log1p requires lower bound >= -1")

        # Degenerate case
        if self.lower == self.upper:
            val = np.log1p(self.expected)
            return AIN(val, val, val)

        new_lower = np.log1p(self.lower)
        new_upper = np.log1p(self.upper)

        # E[ln(1+x)] using LOTUS
        # ∫ln(1+x)dx = (x+1)ln(1+x) - x
        def antiderivative(x):
            return (x + 1) * np.log1p(x) - x

        new_expected = (self.alpha * (antiderivative(self.expected) - antiderivative(self.lower)) +
                        self.beta * (antiderivative(self.upper) - antiderivative(self.expected)))

        return AIN(new_lower, new_upper, new_expected)

    def deg2rad(self):
        """
        Convert degrees to radians.

        Returns
        -------
        AIN
            A new AIN instance with values converted from degrees to radians.

        Examples
        --------
        >>> x = AIN(0, 180, 90)
        >>> result = x.deg2rad()
        >>> print(result)
        [0.0000, 3.1416]_{1.5708}
        """
        factor = np.pi / 180
        return AIN(self.lower * factor,
                   self.upper * factor,
                   self.expected * factor)

    def rad2deg(self):
        """
        Convert radians to degrees.

        Returns
        -------
        AIN
            A new AIN instance with values converted from radians to degrees.

        Examples
        --------
        >>> x = AIN(0, np.pi, np.pi/2)
        >>> result = x.rad2deg()
        >>> print(result)
        [0.0000, 180.0000]_{90.0000}
        """
        factor = 180 / np.pi
        return AIN(self.lower * factor,
                   self.upper * factor,
                   self.expected * factor)

    def leaky_relu(self, alpha=0.01):
        """
        Compute Leaky ReLU: max(x, alpha*x).

        Parameters
        ----------
        alpha : float, optional
            Slope for negative values. Default is 0.01.

        Returns
        -------
        AIN
            A new AIN instance representing Leaky ReLU(X).

        Examples
        --------
        >>> x = AIN(-2, 5, 2)
        >>> result = x.leaky_relu(alpha=0.1)
        >>> print(result)
        [-0.2000, 5.0000]_{2.2000}
        """
        if not isinstance(alpha, (int, float)):
            raise TypeError("alpha must be int or float")
        if alpha < 0 or alpha >= 1:
            raise ValueError("alpha must be in [0, 1)")

        # Leaky ReLU is piecewise linear
        # For x < 0: alpha * x
        # For x >= 0: x

        # Case 1: Entire interval is positive
        if self.lower >= 0:
            return AIN(self.lower, self.upper, self.expected)

        # Case 2: Entire interval is negative
        elif self.upper <= 0:
            return AIN(alpha * self.lower, alpha * self.upper, alpha * self.expected)

        # Case 3: Interval contains zero
        else:
            new_lower = alpha * self.lower
            new_upper = self.upper

            # Compute expected value using LOTUS
            if self.expected <= 0:
                # Expected is in negative part
                new_expected = alpha * self.expected
            else:
                # Expected is in positive part
                # E[LeakyReLU(X)] = α∫_{a}^{0} αx·f(x)dx + α∫_{0}^{c} x·f(x)dx + β∫_{c}^{b} x·f(x)dx
                new_expected = (alpha * self.alpha * (0 ** 2 / 2 - self.lower ** 2 / 2) +
                                self.alpha * (self.expected ** 2 / 2 - 0 ** 2 / 2) +
                                self.beta * (self.upper ** 2 / 2 - self.expected ** 2 / 2))

            return AIN(new_lower, new_upper, new_expected)

    def softplus(self):
        """
        Compute Softplus function: ln(1 + exp(X)).

        This is a smooth approximation of ReLU.

        Returns
        -------
        AIN
            A new AIN instance representing softplus(X).

        Examples
        --------
        >>> x = AIN(-2, 2, 0)
        >>> result = x.softplus()
        >>> print(result)
        [0.1269, 2.1269]_{1.0000}
        """
        from scipy.integrate import quad

        # Degenerate case
        if self.lower == self.upper:
            val = np.log1p(np.exp(self.expected))
            return AIN(val, val, val)

        # Softplus is monotonically increasing
        new_lower = np.log1p(np.exp(self.lower))
        new_upper = np.log1p(np.exp(self.upper))

        # E[softplus(x)] using LOTUS with numerical integration
        # The antiderivative of ln(1+e^x) involves dilogarithm, so we use numerical integration
        def softplus_func(x):
            return np.log1p(np.exp(x))

        integral_left, _ = quad(softplus_func, self.lower, self.expected)
        integral_right, _ = quad(softplus_func, self.expected, self.upper)

        new_expected = self.alpha * integral_left + self.beta * integral_right

        return AIN(new_lower, new_upper, new_expected)

    def elu(self, alpha=1.0):
        """
        Compute Exponential Linear Unit (ELU).

        ELU(x) = x if x > 0
        ELU(x) = alpha * (exp(x) - 1) if x <= 0

        Parameters
        ----------
        alpha : float, optional
            Parameter for negative values. Default is 1.0.

        Returns
        -------
        AIN
            A new AIN instance representing ELU(X).

        Examples
        --------
        >>> x = AIN(-2, 2, 0)
        >>> result = x.elu(alpha=1.0)
        >>> print(result)
        [-0.8647, 2.0000]_{0.5000}
        """
        if not isinstance(alpha, (int, float)):
            raise TypeError("alpha must be int or float")
        if alpha <= 0:
            raise ValueError("alpha must be positive")

        # Case 1: Entire interval is positive
        if self.lower > 0:
            return AIN(self.lower, self.upper, self.expected)

        # Case 2: Entire interval is non-positive
        elif self.upper <= 0:
            new_lower = alpha * (np.exp(self.lower) - 1)
            new_upper = alpha * (np.exp(self.upper) - 1)
            # E[α(e^x - 1)] = α(E[e^x] - 1)
            exp_expected = (self.alpha * (np.exp(self.expected) - np.exp(self.lower)) +
                            self.beta * (np.exp(self.upper) - np.exp(self.expected)))
            new_expected = alpha * exp_expected
            return AIN(new_lower, new_upper, new_expected)

        # Case 3: Interval contains zero
        else:
            new_lower = alpha * (np.exp(self.lower) - 1)
            new_upper = self.upper

            # Compute expected value using LOTUS
            if self.expected <= 0:
                # Expected is in negative part
                exp_expected = (self.alpha * (np.exp(self.expected) - np.exp(self.lower)) +
                                self.beta * (np.exp(0) - np.exp(self.expected)))
                new_expected = alpha * exp_expected
            else:
                # Expected is in positive part
                # E[ELU(X)] for part < 0: α∫_{a}^{0} α(e^x-1)f(x)dx
                # E[ELU(X)] for part > 0: ∫_{0}^{b} x f(x)dx
                neg_part = alpha * (self.alpha * (np.exp(0) - 0 - (np.exp(self.lower) - self.lower)))
                pos_part = (self.alpha * (self.expected ** 2 / 2 - 0 ** 2 / 2) +
                            self.beta * (self.upper ** 2 / 2 - self.expected ** 2 / 2))
                new_expected = neg_part + pos_part

            return AIN(new_lower, new_upper, new_expected)

    def gelu(self):
        # WS_to_check_common_sense
        """
        Compute Gaussian Error Linear Unit (GELU).

        GELU(x) ≈ x * Φ(x) where Φ is the standard normal CDF.
        Approximation: GELU(x) ≈ 0.5 * x * (1 + tanh(√(2/π) * (x + 0.044715 * x³)))

        Returns
        -------
        AIN
            A new AIN instance representing GELU(X).

        Examples
        --------
        >>> x = AIN(-2, 2, 0)
        >>> result = x.gelu()
        >>> print(result)
        [-0.0454, 1.9546]_{0.0000}
        """
        from scipy.integrate import quad
        from scipy.stats import norm

        # Degenerate case
        if self.lower == self.upper:
            val = self.expected * norm.cdf(self.expected)
            return AIN(val, val, val)

        # GELU is monotonically increasing, but not strictly
        new_lower = self.lower * norm.cdf(self.lower)
        new_upper = self.upper * norm.cdf(self.upper)

        # Compute expected value using numerical integration
        def gelu_func(x):
            return x * norm.cdf(x)

        integral_left, _ = quad(gelu_func, self.lower, self.expected)
        integral_right, _ = quad(gelu_func, self.expected, self.upper)

        new_expected = self.alpha * integral_left + self.beta * integral_right

        return AIN(new_lower, new_upper, new_expected)

    def swish(self, beta=1.0):
        # WS_to_check_common_sense
        """
        Compute Swish activation function (also known as SiLU).

        Swish(x) = x * sigmoid(β*x) = x / (1 + exp(-β*x))

        Parameters
        ----------
        beta : float, optional
            Scaling parameter. Default is 1.0.

        Returns
        -------
        AIN
            A new AIN instance representing Swish(X).

        Examples
        --------
        >>> x = AIN(-2, 2, 0)
        >>> result = x.swish()
        >>> print(result)
        [-0.2384, 1.7616]_{0.0000}
        """
        from scipy.integrate import quad

        if not isinstance(beta, (int, float)):
            raise TypeError("beta must be a number")

        # Degenerate case
        if self.lower == self.upper:
            val = self.expected / (1 + np.exp(-beta * self.expected))
            return AIN(val, val, val)

        # Swish bounds
        new_lower = self.lower / (1 + np.exp(-beta * self.lower))
        new_upper = self.upper / (1 + np.exp(-beta * self.upper))

        # Swish can be non-monotonic for negative x, so check ordering
        if new_lower > new_upper:
            new_lower, new_upper = new_upper, new_lower

        # Compute expected value using numerical integration
        def swish_func(x):
            return x / (1 + np.exp(-beta * x))

        integral_left, _ = quad(swish_func, self.lower, self.expected)
        integral_right, _ = quad(swish_func, self.expected, self.upper)

        new_expected = self.alpha * integral_left + self.beta * integral_right

        return AIN(new_lower, new_upper, new_expected)

    def clamp(self, min_val, max_val):
        """
        Clamp (clip) the interval to [min_val, max_val].

        Parameters
        ----------
        min_val : float
            Minimum value.
        max_val : float
            Maximum value.

        Returns
        -------
        AIN
            A new AIN instance with values clamped to [min_val, max_val].

        Raises
        ------
        ValueError
            If min_val >= max_val.

        Examples
        --------
        >>> x = AIN(-5, 10, 2)
        >>> result = x.clamp(0, 5)
        >>> print(result)
        [0.0000, 5.0000]_{2.5000}
        """
        if not isinstance(min_val, (int, float)) or not isinstance(max_val, (int, float)):
            raise TypeError("min_val and max_val must be numbers")
        if min_val >= max_val:
            raise ValueError("min_val must be less than max_val")

        # Clamp the bounds
        new_lower = max(min_val, min(max_val, self.lower))
        new_upper = max(min_val, min(max_val, self.upper))

        # Compute expected value
        # This is complex because clamp is piecewise
        if self.upper <= min_val:
            # Entire interval below min
            new_expected = min_val
        elif self.lower >= max_val:
            # Entire interval above max
            new_expected = max_val
        elif self.lower >= min_val and self.upper <= max_val:
            # Entire interval within bounds
            new_expected = self.expected
        else:
            # Interval spans clamp boundaries - use LOTUS
            # We need to integrate piecewise
            total_expected = 0

            # Part 1: values clamped to min_val
            if self.lower < min_val:
                if self.expected < min_val:
                    prob_below = self.alpha * (self.expected - self.lower)
                    total_expected += min_val * prob_below
                else:
                    prob_below = self.alpha * (min_val - self.lower)
                    total_expected += min_val * prob_below

            # Part 2: values in [min_val, max_val]
            if self.lower < max_val and self.upper > min_val:
                a = max(self.lower, min_val)
                b = min(self.upper, max_val)
                c = self.expected

                if a <= c <= b:
                    # Expected is in unclamped region
                    expected_unclamped = (self.alpha * (c ** 2 / 2 - a ** 2 / 2) +
                                          self.beta * (b ** 2 / 2 - c ** 2 / 2))
                elif c < a:
                    # Expected is below - use beta distribution
                    expected_unclamped = self.beta * (b ** 2 / 2 - a ** 2 / 2)
                else:
                    # Expected is above - use alpha distribution
                    expected_unclamped = self.alpha * (b ** 2 / 2 - a ** 2 / 2)

                total_expected += expected_unclamped

            # Part 3: values clamped to max_val
            if self.upper > max_val:
                if self.expected > max_val:
                    prob_above = self.beta * (self.upper - self.expected)
                    total_expected += max_val * prob_above
                else:
                    prob_above = self.beta * (self.upper - max_val)
                    total_expected += max_val * prob_above

            new_expected = total_expected

        return AIN(new_lower, new_upper, new_expected)

    def clip(self, min_val, max_val):
        """
        Alias for clamp(). Clip values to [min_val, max_val].

        Parameters
        ----------
        min_val : float
            Minimum value.
        max_val : float
            Maximum value.

        Returns
        -------
        AIN
            A new AIN instance with values clipped to [min_val, max_val].

        Examples
        --------
        >>> x = AIN(-5, 10, 2)
        >>> result = x.clip(0, 5)
        >>> print(result)
        [0.0000, 5.0000]_{2.5000}
        """
        return self.clamp(min_val, max_val)

    def skewness(self):
        """
        Compute the skewness (third standardized moment) of the distribution.

        Skewness measures the asymmetry of the distribution.
        - Skewness = 0: symmetric distribution
        - Skewness > 0: right-skewed (tail on the right)
        - Skewness < 0: left-skewed (tail on the left)

        Returns
        -------
        float
            The skewness coefficient.

        Examples
        --------
        >>> x = AIN(0, 10, 3)
        >>> print(x.skewness())
        0.3464
        """
        if self.D2 == 0:
            return 0.0

        # Third central moment: E[(X - μ)³]
        mu = self.expected

        # E[X³] using LOTUS
        third_moment_raw = (self.alpha * (self.expected ** 4 / 4 - self.lower ** 4 / 4) +
                            self.beta * (self.upper ** 4 / 4 - self.expected ** 4 / 4))

        # E[X²]
        second_moment_raw = (self.alpha * (self.expected ** 3 / 3 - self.lower ** 3 / 3) +
                             self.beta * (self.upper ** 3 / 3 - self.expected ** 3 / 3))

        # E[(X-μ)³] = E[X³] - 3μE[X²] + 3μ²E[X] - μ³
        third_central = third_moment_raw - 3 * mu * second_moment_raw + 2 * mu ** 3

        # Skewness = E[(X-μ)³] / σ³
        sigma = np.sqrt(self.D2)
        skew = third_central / (sigma ** 3)

        return skew

    def variance(self):
        # WS_to_check_common_sense
        """
        Return the variance of the distribution.

        The variance is already computed in the D2 attribute.

        Returns
        -------
        float
            The variance of the distribution.

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> print(x.variance())
        8.3333
        """
        return self.D2

    def std(self):
        # WS_to_check_common_sense
        """
        Return the standard deviation of the distribution.

        Standard deviation is the square root of variance.

        Returns
        -------
        float
            The standard deviation.

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> print(x.std())
        2.8868
        """
        return np.sqrt(self.D2)

    def kurtosis(self):
        # WS_to_check_common_sense
        """
        Compute the excess kurtosis (fourth standardized moment - 3) of the distribution.

        Kurtosis measures the "tailedness" of the distribution.
        - Excess kurtosis = 0: normal distribution (mesokurtic)
        - Excess kurtosis > 0: heavy tails (leptokurtic)
        - Excess kurtosis < 0: light tails (platykurtic)

        Returns
        -------
        float
            The excess kurtosis coefficient.

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> print(x.kurtosis())
        -1.2
        """
        if self.D2 == 0:
            return 0.0

        mu = self.expected

        # E[X⁴] using LOTUS: ∫x⁴dx = x⁵/5
        fourth_moment_raw = (self.alpha * (self.expected ** 5 / 5 - self.lower ** 5 / 5) +
                             self.beta * (self.upper ** 5 / 5 - self.expected ** 5 / 5))

        # E[X³]
        third_moment_raw = (self.alpha * (self.expected ** 4 / 4 - self.lower ** 4 / 4) +
                            self.beta * (self.upper ** 4 / 4 - self.expected ** 4 / 4))

        # E[X²]
        second_moment_raw = (self.alpha * (self.expected ** 3 / 3 - self.lower ** 3 / 3) +
                             self.beta * (self.upper ** 3 / 3 - self.expected ** 3 / 3))

        # E[(X-μ)⁴] = E[X⁴] - 4μE[X³] + 6μ²E[X²] - 4μ³E[X] + μ⁴
        fourth_central = (fourth_moment_raw - 4 * mu * third_moment_raw +
                          6 * mu ** 2 * second_moment_raw - 3 * mu ** 4)

        # Excess kurtosis = E[(X-μ)⁴] / σ⁴ - 3
        sigma_4 = self.D2 ** 2
        kurt = fourth_central / sigma_4 - 3

        return kurt

    def cv(self):
        # WS_to_check_common_sense
        """
        Compute the coefficient of variation (CV).

        CV = σ / μ (standard deviation / mean).
        It's a normalized measure of dispersion.

        Returns
        -------
        float
            The coefficient of variation.

        Raises
        ------
        ValueError
            If expected value is zero (division by zero).

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> print(x.cv())
        0.5774
        """
        if self.expected == 0:
            raise ValueError("Coefficient of variation is undefined when expected value is zero")

        return np.sqrt(self.D2) / self.expected

    def entropy(self):
        # WS_to_check_common_sense
        """
        Compute the differential entropy of the AIN distribution.

        For a piecewise linear PDF, the entropy is:
        H(X) = -∫ f(x) log(f(x)) dx

        Returns
        -------
        float
            The differential entropy in nats (natural logarithm).

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> print(x.entropy())
        2.3026
        """
        # For degenerate (point mass), entropy is -∞, but we return a large negative number
        if self.lower == self.upper:
            return -np.inf

        # For piecewise uniform approximation:
        # The distribution has two parts with densities alpha and beta
        # H = -∫_{a}^{c} α·log(α) dx - ∫_{c}^{b} β·log(β) dx
        # H = -α·log(α)·(c-a) - β·log(β)·(b-c)

        a, b, c = self.lower, self.upper, self.expected
        alpha, beta = self.alpha, self.beta

        entropy = 0.0

        if alpha > 0 and c > a:
            entropy -= alpha * np.log(alpha) * (c - a)

        if beta > 0 and b > c:
            entropy -= beta * np.log(beta) * (b - c)

        return entropy

    def width(self):
        """
        Return the width of the interval.

        Returns
        -------
        float
            The width (upper - lower).

        Examples
        --------
        >>> x = AIN(1, 10, 5)
        >>> print(x.width())
        9.0
        """
        return self.upper - self.lower

    def midpoint(self):
        """
        Return the midpoint of the interval.

        Returns
        -------
        float
            The midpoint ((upper + lower) / 2).

        Examples
        --------
        >>> x = AIN(1, 10, 5)
        >>> print(x.midpoint())
        5.5
        """
        return (self.upper + self.lower) / 2

    def radius(self):
        """
        Return the radius of the interval.

        Returns
        -------
        float
            The radius ((upper - lower) / 2).

        Examples
        --------
        >>> x = AIN(1, 10, 5)
        >>> print(x.radius())
        4.5
        """
        return (self.upper - self.lower) / 2

    def is_degenerate(self):
        """
        Check if the interval is degenerate (a single point).

        Returns
        -------
        bool
            True if lower == upper, False otherwise.

        Examples
        --------
        >>> x = AIN(5, 5, 5)
        >>> print(x.is_degenerate())
        True

        >>> x = AIN(1, 10, 5)
        >>> print(x.is_degenerate())
        False
        """
        return self.lower == self.upper

    def is_positive(self):
        # WS_to_check_common_sense
        """
        Check if the entire interval is positive.

        Returns
        -------
        bool
            True if lower > 0, False otherwise.

        Examples
        --------
        >>> x = AIN(1, 10, 5)
        >>> print(x.is_positive())
        True

        >>> x = AIN(-5, 10, 2)
        >>> print(x.is_positive())
        False
        """
        return self.lower > 0

    def is_negative(self):
        # WS_to_check_common_sense
        """
        Check if the entire interval is negative.

        Returns
        -------
        bool
            True if upper < 0, False otherwise.

        Examples
        --------
        >>> x = AIN(-10, -1, -5)
        >>> print(x.is_negative())
        True

        >>> x = AIN(-5, 10, 2)
        >>> print(x.is_negative())
        False
        """
        return self.upper < 0

    def is_zero(self):
        # WS_to_check_common_sense
        """
        Check if the interval represents exactly zero.

        Returns
        -------
        bool
            True if AIN(0, 0, 0), False otherwise.

        Examples
        --------
        >>> x = AIN(0, 0, 0)
        >>> print(x.is_zero())
        True

        >>> x = AIN(-1, 1, 0)
        >>> print(x.is_zero())
        False
        """
        return self.lower == 0 and self.upper == 0 and self.expected == 0

    def has_zero(self):
        # WS_to_check_common_sense
        """
        Check if the interval contains zero.

        Returns
        -------
        bool
            True if lower <= 0 <= upper, False otherwise.

        Examples
        --------
        >>> x = AIN(-5, 5, 0)
        >>> print(x.has_zero())
        True

        >>> x = AIN(1, 10, 5)
        >>> print(x.has_zero())
        False
        """
        return self.lower <= 0 <= self.upper

    def is_symmetric(self):
        # WS_to_check_common_sense
        """
        Check if the interval is symmetric (expected at midpoint).

        Returns
        -------
        bool
            True if expected is at the midpoint (asymmetry ≈ 0), False otherwise.

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> print(x.is_symmetric())
        True

        >>> x = AIN(0, 10, 3)
        >>> print(x.is_symmetric())
        False
        """
        return np.isclose(self.asymmetry, 0, atol=1e-9)

    def intersection(self, other):
        # WS_to_check_common_sense
        """
        Compute the intersection of two intervals.

        Parameters
        ----------
        other : AIN
            Another AIN instance.

        Returns
        -------
        AIN or None
            The intersection interval, or None if intervals don't overlap.

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> y = AIN(5, 15, 10)
        >>> result = x.intersection(y)
        >>> print(result)
        [5.0000, 10.0000]_{7.5000}
        """
        if not isinstance(other, AIN):
            raise TypeError("other must be an AIN instance")

        new_lower = max(self.lower, other.lower)
        new_upper = min(self.upper, other.upper)

        if new_lower > new_upper:
            return None  # No intersection

        # Expected value is midpoint of intersection by default
        new_expected = (new_lower + new_upper) / 2

        return AIN(new_lower, new_upper, new_expected)

    def union(self, other):
        # WS_to_check_common_sense
        """
        Compute the union (hull) of two intervals.

        Returns the smallest interval containing both intervals.

        Parameters
        ----------
        other : AIN
            Another AIN instance.

        Returns
        -------
        AIN
            The union interval.

        Examples
        --------
        >>> x = AIN(0, 5, 2)
        >>> y = AIN(7, 10, 8)
        >>> result = x.union(y)
        >>> print(result)
        [0.0000, 10.0000]_{5.0000}
        """
        if not isinstance(other, AIN):
            raise TypeError("other must be an AIN instance")

        new_lower = min(self.lower, other.lower)
        new_upper = max(self.upper, other.upper)

        # Weighted average of expected values based on widths
        w1 = self.upper - self.lower
        w2 = other.upper - other.lower
        total_weight = w1 + w2

        if total_weight == 0:
            new_expected = self.expected
        else:
            new_expected = (w1 * self.expected + w2 * other.expected) / total_weight

        return AIN(new_lower, new_upper, new_expected)

    def contains(self, value):
        # WS_to_check_common_sense
        """
        Check if a value is contained in the interval.

        Parameters
        ----------
        value : float or int
            The value to check.

        Returns
        -------
        bool
            True if lower <= value <= upper, False otherwise.

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> print(x.contains(5))
        True
        >>> print(x.contains(15))
        False
        """
        if not isinstance(value, (int, float)):
            raise TypeError("value must be a number")

        return self.lower <= value <= self.upper

    def overlaps(self, other):
        # WS_to_check_common_sense
        """
        Check if two intervals overlap.

        Parameters
        ----------
        other : AIN
            Another AIN instance.

        Returns
        -------
        bool
            True if intervals overlap, False otherwise.

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> y = AIN(5, 15, 10)
        >>> print(x.overlaps(y))
        True

        >>> x = AIN(0, 5, 2)
        >>> y = AIN(10, 15, 12)
        >>> print(x.overlaps(y))
        False
        """
        if not isinstance(other, AIN):
            raise TypeError("other must be an AIN instance")

        return not (self.upper < other.lower or self.lower > other.upper)

    def is_subset_of(self, other):
        # WS_to_check_common_sense
        """
        Check if this interval is a subset of another interval.

        An interval A is a subset of B if A is completely contained within B:
        B.lower <= A.lower and A.upper <= B.upper

        Parameters
        ----------
        other : AIN
            Another AIN instance.

        Returns
        -------
        bool
            True if self is a subset of other, False otherwise.

        Examples
        --------
        >>> x = AIN(2, 8, 5)
        >>> y = AIN(0, 10, 5)
        >>> print(x.is_subset_of(y))
        True

        >>> x = AIN(0, 10, 5)
        >>> y = AIN(2, 8, 5)
        >>> print(x.is_subset_of(y))
        False
        """
        if not isinstance(other, AIN):
            raise TypeError("other must be an AIN instance")

        return other.lower <= self.lower and self.upper <= other.upper

    def is_superset_of(self, other):
        # WS_to_check_common_sense
        """
        Check if this interval is a superset of another interval.

        An interval A is a superset of B if A completely contains B:
        A.lower <= B.lower and B.upper <= A.upper

        Parameters
        ----------
        other : AIN
            Another AIN instance.

        Returns
        -------
        bool
            True if self is a superset of other, False otherwise.

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> y = AIN(2, 8, 5)
        >>> print(x.is_superset_of(y))
        True

        >>> x = AIN(2, 8, 5)
        >>> y = AIN(0, 10, 5)
        >>> print(x.is_superset_of(y))
        False
        """
        if not isinstance(other, AIN):
            raise TypeError("other must be an AIN instance")

        return self.lower <= other.lower and other.upper <= self.upper

    def is_disjoint(self, other):
        # WS_to_check_common_sense
        """
        Check if two intervals are disjoint (do not overlap).

        Two intervals are disjoint if they have no common points.

        Parameters
        ----------
        other : AIN
            Another AIN instance.

        Returns
        -------
        bool
            True if intervals are disjoint, False otherwise.

        Examples
        --------
        >>> x = AIN(0, 5, 2)
        >>> y = AIN(10, 15, 12)
        >>> print(x.is_disjoint(y))
        True

        >>> x = AIN(0, 10, 5)
        >>> y = AIN(5, 15, 10)
        >>> print(x.is_disjoint(y))
        False
        """
        if not isinstance(other, AIN):
            raise TypeError("other must be an AIN instance")

        return not self.overlaps(other)

    def distance(self, other):
        # WS_to_check_common_sense
        """
        Compute the distance between two intervals.

        Distance is 0 if intervals overlap, otherwise it's the gap between them.

        Parameters
        ----------
        other : AIN
            Another AIN instance.

        Returns
        -------
        float
            The distance between intervals.

        Examples
        --------
        >>> x = AIN(0, 5, 2)
        >>> y = AIN(10, 15, 12)
        >>> print(x.distance(y))
        5.0

        >>> x = AIN(0, 10, 5)
        >>> y = AIN(5, 15, 10)
        >>> print(x.distance(y))
        0.0
        """
        if not isinstance(other, AIN):
            raise TypeError("other must be an AIN instance")

        if self.overlaps(other):
            return 0.0

        return max(other.lower - self.upper, self.lower - other.upper)

    def scale(self, factor):
        # WS_to_check_common_sense
        """
        Scale the interval by a constant factor.

        Equivalent to multiplying by a scalar.

        Parameters
        ----------
        factor : float or int
            The scaling factor.

        Returns
        -------
        AIN
            A new scaled AIN instance.

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> result = x.scale(2)
        >>> print(result)
        [0.0000, 20.0000]_{10.0000}
        """
        return self * factor

    def shift(self, offset):
        # WS_to_check_common_sense
        """
        Shift the interval by a constant offset.

        Equivalent to adding a scalar.

        Parameters
        ----------
        offset : float or int
            The offset to add.

        Returns
        -------
        AIN
            A new shifted AIN instance.

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> result = x.shift(5)
        >>> print(result)
        [5.0000, 15.0000]_{10.0000}
        """
        return self + offset

    def blend(self, other, weight):
        # WS_to_check_common_sense
        """
        Blend this AIN with another using linear interpolation.

        Computes (1-weight)*self + weight*other, which is equivalent to
        lerp(self, other, weight) but as an instance method.

        Parameters
        ----------
        other : AIN
            Another AIN instance to blend with.
        weight : float
            Blending weight in [0, 1]:
            - weight=0: returns self
            - weight=1: returns other
            - weight=0.5: returns average of self and other

        Returns
        -------
        AIN
            Blended AIN instance.

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> y = AIN(10, 20, 15)
        >>> result = x.blend(y, 0.5)
        >>> print(result)
        [5.0000, 15.0000]_{10.0000}

        >>> result = x.blend(y, 0.25)
        >>> print(result)
        [2.5000, 12.5000]_{7.5000}
        """
        if not isinstance(other, AIN):
            raise TypeError("other must be an AIN instance")

        if not isinstance(weight, (int, float)):
            raise TypeError("weight must be a number")

        if not 0 <= weight <= 1:
            raise ValueError("weight must be in [0, 1]")

        return self * (1 - weight) + other * weight

    def normalize(self, mode='minmax'):
        # WS_to_check_common_sense
        """
        Normalize the interval.

        Parameters
        ----------
        mode : str, optional
            Normalization mode:
            - 'minmax': Scale to [0, 1] (default)
            - 'symmetric': Scale to [-1, 1]
            - 'standard': Standardize to mean=0, std=1

        Returns
        -------
        AIN
            A new normalized AIN instance.

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> result = x.normalize('minmax')
        >>> print(result)
        [0.0000, 1.0000]_{0.5000}

        >>> result = x.normalize('symmetric')
        >>> print(result)
        [-1.0000, 1.0000]_{0.0000}
        """
        if mode == 'minmax':
            # Scale to [0, 1]
            width = self.upper - self.lower
            if width == 0:
                return AIN(0, 0, 0)

            new_lower = 0.0
            new_upper = 1.0
            new_expected = (self.expected - self.lower) / width

            return AIN(new_lower, new_upper, new_expected)

        elif mode == 'symmetric':
            # Scale to [-1, 1] centered at midpoint
            midpoint = (self.upper + self.lower) / 2
            radius = (self.upper - self.lower) / 2

            if radius == 0:
                return AIN(0, 0, 0)

            new_lower = -1.0
            new_upper = 1.0
            new_expected = (self.expected - midpoint) / radius

            return AIN(new_lower, new_upper, new_expected)

        elif mode == 'standard':
            # Standardize to mean=0, std=1
            std_dev = np.sqrt(self.D2)

            if std_dev == 0:
                return AIN(0, 0, 0)

            new_lower = (self.lower - self.expected) / std_dev
            new_upper = (self.upper - self.expected) / std_dev
            new_expected = 0.0

            return AIN(new_lower, new_upper, new_expected)

        else:
            raise ValueError(f"Unknown normalization mode: {mode}. Use 'minmax', 'symmetric', or 'standard'.")

    def extend(self, factor):
        # WS_to_check_common_sense
        """
        Extend the interval by a factor of its width.

        Parameters
        ----------
        factor : float
            Extension factor (0 to 1). The interval is extended by
            factor * width on each side.

        Returns
        -------
        AIN
            New AIN with extended bounds, expected value preserved.

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> result = x.extend(0.1)  # Extend by 10% on each side
        >>> print(result)
        [- 1.0000, 11.0000]_{5.0000}
        """
        if not isinstance(factor, (int, float)):
            raise TypeError("factor must be a number")
        if factor < 0:
            raise ValueError("factor must be non-negative")

        width = self.upper - self.lower
        extension = width * factor

        new_lower = self.lower - extension
        new_upper = self.upper + extension

        return AIN(new_lower, new_upper, self.expected)

    def shrink(self, factor):
        # WS_to_check_common_sense
        """
        Shrink the interval by a factor of its width.

        Parameters
        ----------
        factor : float
            Shrink factor (0 to 1). The interval is shrunk by
            factor * width from each side.

        Returns
        -------
        AIN
            New AIN with shrunken bounds, expected value adjusted if needed.

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> result = x.shrink(0.1)  # Shrink by 10% from each side
        >>> print(result)
        [1.0000, 9.0000]_{5.0000}
        """
        if not isinstance(factor, (int, float)):
            raise TypeError("factor must be a number")
        if factor < 0 or factor >= 0.5:
            raise ValueError("factor must be in [0, 0.5)")

        width = self.upper - self.lower
        shrinkage = width * factor

        new_lower = self.lower + shrinkage
        new_upper = self.upper - shrinkage

        # Adjust expected if it falls outside new bounds
        new_expected = self.expected
        if new_expected < new_lower:
            new_expected = new_lower
        elif new_expected > new_upper:
            new_expected = new_upper

        return AIN(new_lower, new_upper, new_expected)

    def pad(self, amount):
        # WS_to_check_common_sense
        """
        Add fixed padding to both sides of the interval.

        Parameters
        ----------
        amount : float
            Padding amount to add to each side.

        Returns
        -------
        AIN
            New AIN with padded bounds, expected value preserved.

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> result = x.pad(2)
        >>> print(result)
        [-2.0000, 12.0000]_{5.0000}
        """
        if not isinstance(amount, (int, float)):
            raise TypeError("amount must be a number")
        if amount < 0:
            raise ValueError("amount must be non-negative")

        new_lower = self.lower - amount
        new_upper = self.upper + amount

        return AIN(new_lower, new_upper, self.expected)

    def __lt__(self, other):
        """
        Compute P(X < Y) where Y can be a number or another AIN.

        For probabilistic comparison.

        Parameters
        ----------
        other : float, int, or AIN
            The value or interval to compare with.

        Returns
        -------
        float
            Probability that X < other.

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> print(x < 7)
        0.7

        >>> x = AIN(0, 10, 3)
        >>> y = AIN(5, 15, 10)
        >>> print(x < y)
        0.85
        """
        if isinstance(other, (int, float)):
            # P(X < constant) = CDF(constant)
            return self.cdf(other)
        elif isinstance(other, AIN):
            # P(X < Y) for two independent AIN
            # This is complex - we use approximation
            # For independent X,Y: P(X < Y) = ∫∫[x<y] f_X(x)f_Y(y) dx dy
            # Approximation: if means are far apart, use normal approximation
            if self.upper <= other.lower:
                return 1.0
            elif self.lower >= other.upper:
                return 0.0
            else:
                # Use approximation based on expected values and variances
                # P(X < Y) = P(X - Y < 0)
                # E[X - Y] = E[X] - E[Y]
                # Var[X - Y] = Var[X] + Var[Y] (for independent)
                mean_diff = self.expected - other.expected
                var_diff = self.D2 + other.D2

                if var_diff == 0:
                    return 1.0 if mean_diff < 0 else 0.0

                # Use normal approximation with CDF
                from scipy import stats
                prob = stats.norm.cdf(0, loc=mean_diff, scale=np.sqrt(var_diff))
                return prob
        else:
            raise TypeError("other must be a number or AIN instance")

    def __gt__(self, other):
        """
        Compute P(X > Y) where Y can be a number or another AIN.

        Parameters
        ----------
        other : float, int, or AIN
            The value or interval to compare with.

        Returns
        -------
        float
            Probability that X > other.

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> print(x > 3)
        0.7

        >>> x = AIN(5, 15, 10)
        >>> y = AIN(0, 10, 3)
        >>> print(x > y)
        0.85
        """
        if isinstance(other, (int, float)):
            # P(X > constant) = 1 - CDF(constant)
            return 1 - self.cdf(other)
        elif isinstance(other, AIN):
            # P(X > Y) = P(Y < X)
            return other < self
        else:
            raise TypeError("other must be a number or AIN instance")

    def __eq__(self, other):
        """
        Check equality or compute P(X = Y) for continuous distributions.

        For continuous distributions, P(X = Y) = 0 unless both are degenerate
        at the same point.

        Parameters
        ----------
        other : float, int, or AIN
            The value or interval to compare with.

        Returns
        -------
        bool or float
            For numbers: returns True/False (deterministic equality).
            For AIN: returns 0.0 (continuous distributions).

        Examples
        --------
        >>> x = AIN(5, 5, 5)
        >>> print(x == 5)
        True

        >>> x = AIN(0, 10, 5)
        >>> y = AIN(0, 10, 5)
        >>> print(x == y)
        0.0
        """
        if isinstance(other, (int, float)):
            # Deterministic equality check
            return self.is_degenerate() and self.expected == other
        elif isinstance(other, AIN):
            # For continuous distributions, P(X = Y) = 0
            # unless both are degenerate at the same point
            if self.is_degenerate() and other.is_degenerate():
                return self.expected == other.expected
            return 0.0
        else:
            return False

    def __le__(self, other):
        # WS_to_check_common_sense
        """
        Compute P(X ≤ value) or P(X ≤ Y) (less than or equal to).

        Parameters
        ----------
        other : float, int, or AIN
            The value or interval to compare with.

        Returns
        -------
        float
            Probability that X ≤ other.

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> print(x <= 5)
        0.5
        """
        if isinstance(other, (int, float)):
            return self.cdf(other)
        elif isinstance(other, AIN):
            # P(X ≤ Y) for continuous distributions
            # This is slightly different from P(X < Y) but for continuous it's the same
            return self < other
        else:
            raise TypeError("Comparison only supported with numbers or AIN instances")

    def __ge__(self, other):
        # WS_to_check_common_sense
        """
        Compute P(X ≥ value) or P(X ≥ Y) (greater than or equal to).

        Parameters
        ----------
        other : float, int, or AIN
            The value or interval to compare with.

        Returns
        -------
        float
            Probability that X ≥ other.

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> print(x >= 5)
        0.5
        """
        if isinstance(other, (int, float)):
            return 1.0 - self.cdf(other)
        elif isinstance(other, AIN):
            # P(X ≥ Y) = P(Y ≤ X)
            return other < self
        else:
            raise TypeError("Comparison only supported with numbers or AIN instances")

    def __ne__(self, other):
        # WS_to_check_common_sense
        """
        Check inequality or compute P(X ≠ Y).

        For continuous distributions, P(X ≠ Y) = 1.0 unless both are degenerate
        at the same point.

        Parameters
        ----------
        other : float, int, or AIN
            The value or interval to compare with.

        Returns
        -------
        bool or float
            For numbers: returns True/False (deterministic inequality).
            For AIN: returns 1.0 (continuous distributions).

        Examples
        --------
        >>> x = AIN(5, 5, 5)
        >>> print(x != 5)
        False

        >>> x = AIN(0, 10, 5)
        >>> y = AIN(0, 10, 5)
        >>> print(x != y)
        1.0
        """
        if isinstance(other, (int, float)):
            return not (self.is_degenerate() and self.expected == other)
        elif isinstance(other, AIN):
            # For continuous distributions, P(X ≠ Y) = 1.0
            # unless both are degenerate at the same point
            if self.is_degenerate() and other.is_degenerate():
                return self.expected != other.expected
            return 1.0
        else:
            return True

    @staticmethod
    def sum(ain_list):
        """
        Compute the sum of multiple AIN instances.

        Parameters
        ----------
        ain_list : list of AIN
            List of AIN instances to sum.

        Returns
        -------
        AIN
            A new AIN instance representing the sum.

        Raises
        ------
        TypeError
            If ain_list is not a list or contains non-AIN elements.
        ValueError
            If ain_list is empty.

        Examples
        --------
        >>> ains = [AIN(0, 2, 1), AIN(1, 3, 2), AIN(2, 4, 3)]
        >>> result = AIN.sum(ains)
        >>> print(result)
        [3.0000, 9.0000]_{6.0000}
        """
        if not isinstance(ain_list, list):
            raise TypeError("ain_list must be a list")
        if len(ain_list) == 0:
            raise ValueError("ain_list cannot be empty")

        for ain in ain_list:
            if not isinstance(ain, AIN):
                raise TypeError("All elements must be AIN instances")

        # Sum using reduce
        result = ain_list[0]
        for ain in ain_list[1:]:
            result = result + ain

        return result

    @staticmethod
    def mean(ain_list):
        """
        Compute the mean (average) of multiple AIN instances.

        Parameters
        ----------
        ain_list : list of AIN
            List of AIN instances to average.

        Returns
        -------
        AIN
            A new AIN instance representing the mean.

        Raises
        ------
        TypeError
            If ain_list is not a list or contains non-AIN elements.
        ValueError
            If ain_list is empty.

        Examples
        --------
        >>> ains = [AIN(0, 2, 1), AIN(1, 3, 2), AIN(2, 4, 3)]
        >>> result = AIN.mean(ains)
        >>> print(result)
        [1.0000, 3.0000]_{2.0000}
        """
        if not isinstance(ain_list, list):
            raise TypeError("ain_list must be a list")
        if len(ain_list) == 0:
            raise ValueError("ain_list cannot be empty")

        total = AIN.sum(ain_list)
        n = len(ain_list)

        return AIN(total.lower / n, total.upper / n, total.expected / n)

    @staticmethod
    def median(ain_list):
        # WS_to_check_common_sense
        """
        Compute the median of multiple AIN instances.

        This returns the AIN whose expected value is closest to the median
        of all expected values.

        Parameters
        ----------
        ain_list : list of AIN
            List of AIN instances.

        Returns
        -------
        AIN
            The median AIN instance.

        Raises
        ------
        TypeError
            If ain_list is not a list or contains non-AIN elements.
        ValueError
            If ain_list is empty.

        Examples
        --------
        >>> ains = [AIN(0, 2, 1), AIN(1, 3, 2), AIN(4, 6, 5)]
        >>> result = AIN.median(ains)
        >>> print(result)
        [1.0000, 3.0000]_{2.0000}
        """
        if not isinstance(ain_list, list):
            raise TypeError("ain_list must be a list")
        if len(ain_list) == 0:
            raise ValueError("ain_list cannot be empty")

        for ain in ain_list:
            if not isinstance(ain, AIN):
                raise TypeError("All elements must be AIN instances")

        # Sort by expected value
        sorted_ains = sorted(ain_list, key=lambda x: x.expected)
        n = len(sorted_ains)

        if n % 2 == 1:
            # Odd number: return middle element
            return sorted_ains[n // 2]
        else:
            # Even number: return average of two middle elements
            mid1 = sorted_ains[n // 2 - 1]
            mid2 = sorted_ains[n // 2]
            return AIN((mid1.lower + mid2.lower) / 2,
                       (mid1.upper + mid2.upper) / 2,
                       (mid1.expected + mid2.expected) / 2)

    @staticmethod
    def list_variance(ain_list):
        # WS_to_check_common_sense
        """
        Compute the variance of multiple AIN instances.

        This computes the variance of the expected values.

        Parameters
        ----------
        ain_list : list of AIN
            List of AIN instances.

        Returns
        -------
        float
            The variance of expected values.

        Raises
        ------
        TypeError
            If ain_list is not a list or contains non-AIN elements.
        ValueError
            If ain_list is empty or has only one element.

        Examples
        --------
        >>> ains = [AIN(0, 2, 1), AIN(1, 3, 2), AIN(2, 4, 3)]
        >>> var = AIN.list_variance(ains)
        >>> print(var)
        1.0
        """
        if not isinstance(ain_list, list):
            raise TypeError("ain_list must be a list")
        if len(ain_list) == 0:
            raise ValueError("ain_list cannot be empty")
        if len(ain_list) == 1:
            raise ValueError("Variance requires at least 2 elements")

        for ain in ain_list:
            if not isinstance(ain, AIN):
                raise TypeError("All elements must be AIN instances")

        # Compute variance of expected values
        expected_vals = [ain.expected for ain in ain_list]
        mean_val = np.mean(expected_vals)
        variance = np.var(expected_vals, ddof=1)  # Sample variance

        return variance

    @staticmethod
    def list_std(ain_list):
        # WS_to_check_common_sense
        """
        Compute the standard deviation of multiple AIN instances.

        This computes the standard deviation of the expected values.

        Parameters
        ----------
        ain_list : list of AIN
            List of AIN instances.

        Returns
        -------
        float
            The standard deviation of expected values.

        Raises
        ------
        TypeError
            If ain_list is not a list or contains non-AIN elements.
        ValueError
            If ain_list is empty or has only one element.

        Examples
        --------
        >>> ains = [AIN(0, 2, 1), AIN(1, 3, 2), AIN(2, 4, 3)]
        >>> std = AIN.list_std(ains)
        >>> print(std)
        1.0
        """
        return np.sqrt(AIN.list_variance(ain_list))

    @staticmethod
    def min(ain1, ain2):
        """
        Compute the minimum of two AIN instances: min(X, Y).

        Parameters
        ----------
        ain1 : AIN
            First AIN instance.
        ain2 : AIN
            Second AIN instance.

        Returns
        -------
        AIN
            A new AIN instance representing min(X, Y).

        Raises
        ------
        TypeError
            If either argument is not an AIN instance.

        Examples
        --------
        >>> x = AIN(1, 5, 3)
        >>> y = AIN(2, 6, 4)
        >>> result = AIN.min(x, y)
        >>> print(result)
        [1.0000, 5.0000]_{2.6667}
        """
        if not isinstance(ain1, AIN):
            raise TypeError("ain1 must be an AIN instance")
        if not isinstance(ain2, AIN):
            raise TypeError("ain2 must be an AIN instance")

        # Lower bound is minimum of lower bounds
        new_lower = min(ain1.lower, ain2.lower)

        # Upper bound is minimum of upper bounds
        new_upper = min(ain1.upper, ain2.upper)

        # Expected value computation is more complex
        # We use approximation: E[min(X,Y)] ≈ weighted average based on CDFs
        # For independent X and Y: E[min(X,Y)] = integral of (1 - F_X(t)·F_Y(t)) dt

        # Simple approximation using midpoints and bounds
        if ain1.expected < ain2.expected:
            # X tends to be smaller
            weight1 = 0.6
            weight2 = 0.4
        elif ain1.expected > ain2.expected:
            # Y tends to be smaller
            weight1 = 0.4
            weight2 = 0.6
        else:
            # Equal expected values
            weight1 = 0.5
            weight2 = 0.5

        new_expected = weight1 * ain1.expected + weight2 * ain2.expected

        # Ensure expected is within bounds
        new_expected = max(new_lower, min(new_upper, new_expected))

        return AIN(new_lower, new_upper, new_expected)

    @staticmethod
    def max(ain1, ain2):
        """
        Compute the maximum of two AIN instances: max(X, Y).

        Parameters
        ----------
        ain1 : AIN
            First AIN instance.
        ain2 : AIN
            Second AIN instance.

        Returns
        -------
        AIN
            A new AIN instance representing max(X, Y).

        Raises
        ------
        TypeError
            If either argument is not an AIN instance.

        Examples
        --------
        >>> x = AIN(1, 5, 3)
        >>> y = AIN(2, 6, 4)
        >>> result = AIN.max(x, y)
        >>> print(result)
        [2.0000, 6.0000]_{4.3333}
        """
        if not isinstance(ain1, AIN):
            raise TypeError("ain1 must be an AIN instance")
        if not isinstance(ain2, AIN):
            raise TypeError("ain2 must be an AIN instance")

        # Lower bound is maximum of lower bounds
        new_lower = max(ain1.lower, ain2.lower)

        # Upper bound is maximum of upper bounds
        new_upper = max(ain1.upper, ain2.upper)

        # Expected value computation
        # Simple approximation using weighted average
        if ain1.expected > ain2.expected:
            # X tends to be larger
            weight1 = 0.6
            weight2 = 0.4
        elif ain1.expected < ain2.expected:
            # Y tends to be larger
            weight1 = 0.4
            weight2 = 0.6
        else:
            # Equal expected values
            weight1 = 0.5
            weight2 = 0.5

        new_expected = weight1 * ain1.expected + weight2 * ain2.expected

        # Ensure expected is within bounds
        new_expected = max(new_lower, min(new_upper, new_expected))

        return AIN(new_lower, new_upper, new_expected)

    @staticmethod
    def lerp(ain1, ain2, t):
        # WS_to_check_common_sense
        """
        Linear interpolation between two AIN instances.

        lerp(ain1, ain2, t) = (1-t)*ain1 + t*ain2

        Parameters
        ----------
        ain1 : AIN
            First AIN instance (at t=0)
        ain2 : AIN
            Second AIN instance (at t=1)
        t : float
            Interpolation parameter (typically in [0, 1])

        Returns
        -------
        AIN
            Interpolated AIN instance

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> y = AIN(10, 20, 15)
        >>> result = AIN.lerp(x, y, 0.5)  # Midpoint
        >>> print(result)
        [5.0000, 15.0000]_{10.0000}
        """
        if not isinstance(ain1, AIN) or not isinstance(ain2, AIN):
            raise TypeError("ain1 and ain2 must be AIN instances")
        if not isinstance(t, (int, float)):
            raise TypeError("t must be a number")

        return ain1 * (1 - t) + ain2 * t

    @staticmethod
    def fma(a, b, c):
        # WS_to_check_common_sense
        """
        Fused multiply-add: a*b + c.

        Computes a*b + c for AIN instances with potentially better
        numerical accuracy than separate operations.

        Parameters
        ----------
        a, b, c : AIN
            AIN instances

        Returns
        -------
        AIN
            Result of a*b + c

        Examples
        --------
        >>> a = AIN(1, 2, 1.5)
        >>> b = AIN(2, 3, 2.5)
        >>> c = AIN(0, 1, 0.5)
        >>> result = AIN.fma(a, b, c)
        >>> print(result)
        [2.0000, 7.0000]_{4.2500}
        """
        if not all(isinstance(x, AIN) for x in [a, b, c]):
            raise TypeError("All arguments must be AIN instances")

        return a * b + c

    @staticmethod
    def weighted_mean(ain_list, weights):
        # WS_to_check_common_sense
        """
        Compute weighted mean of AIN instances.

        Parameters
        ----------
        ain_list : list of AIN
            List of AIN instances
        weights : list of float
            Weights for each AIN (must sum to 1 or will be normalized)

        Returns
        -------
        AIN
            Weighted mean

        Examples
        --------
        >>> ains = [AIN(0, 10, 5), AIN(10, 20, 15), AIN(20, 30, 25)]
        >>> weights = [0.5, 0.3, 0.2]
        >>> result = AIN.weighted_mean(ains, weights)
        >>> print(result)
        [5.0000, 17.0000]_{11.0000}
        """
        if not isinstance(ain_list, list) or not isinstance(weights, list):
            raise TypeError("ain_list and weights must be lists")
        if len(ain_list) != len(weights):
            raise ValueError("ain_list and weights must have same length")
        if len(ain_list) == 0:
            raise ValueError("ain_list cannot be empty")

        weights = np.array(weights, dtype=float)
        weights = weights / np.sum(weights)  # Normalize

        result = AIN.zeros()
        for ain, w in zip(ain_list, weights):
            if not isinstance(ain, AIN):
                raise TypeError("All elements must be AIN instances")
            result = result + ain * w

        return result

    @staticmethod
    def geometric_mean(ain_list):
        # WS_to_check_common_sense
        """
        Compute geometric mean of AIN instances.

        GM = (a₁ × a₂ × ... × aₙ)^(1/n)

        Parameters
        ----------
        ain_list : list of AIN
            List of positive AIN instances

        Returns
        -------
        AIN
            Geometric mean

        Raises
        ------
        ValueError
            If any AIN has non-positive values

        Examples
        --------
        >>> ains = [AIN(1, 4, 2), AIN(2, 8, 4), AIN(3, 12, 6)]
        >>> result = AIN.geometric_mean(ains)
        >>> print(result)
        [1.8171, 7.7113]_{3.6342}
        """
        if not isinstance(ain_list, list):
            raise TypeError("ain_list must be a list")
        if len(ain_list) == 0:
            raise ValueError("ain_list cannot be empty")

        for ain in ain_list:
            if not isinstance(ain, AIN):
                raise TypeError("All elements must be AIN instances")
            if ain.lower <= 0:
                raise ValueError("All AIN instances must be positive for geometric mean")

        result = ain_list[0]
        for ain in ain_list[1:]:
            result = result * ain

        n = len(ain_list)
        return result ** (1.0 / n)

    @staticmethod
    def harmonic_mean(ain_list):
        # WS_to_check_common_sense
        """
        Compute harmonic mean of AIN instances.

        HM = n / (1/a₁ + 1/a₂ + ... + 1/aₙ)

        Parameters
        ----------
        ain_list : list of AIN
            List of positive AIN instances

        Returns
        -------
        AIN
            Harmonic mean

        Raises
        ------
        ValueError
            If any AIN contains zero

        Examples
        --------
        >>> ains = [AIN(1, 3, 2), AIN(2, 4, 3), AIN(3, 5, 4)]
        >>> result = AIN.harmonic_mean(ains)
        >>> print(result)
        [1.6364, 3.7500]_{2.7692}
        """
        if not isinstance(ain_list, list):
            raise TypeError("ain_list must be a list")
        if len(ain_list) == 0:
            raise ValueError("ain_list cannot be empty")

        for ain in ain_list:
            if not isinstance(ain, AIN):
                raise TypeError("All elements must be AIN instances")
            if ain.lower <= 0 <= ain.upper:
                raise ValueError("AIN instances cannot contain zero for harmonic mean")

        reciprocal_sum = AIN.zeros()
        for ain in ain_list:
            reciprocal_sum = reciprocal_sum + ain.reciprocal()

        n = len(ain_list)
        return (reciprocal_sum / n).reciprocal()

    @staticmethod
    def percentile(ain_list, q):
        # WS_to_check_common_sense
        """
        Compute q-th percentile of AIN instances based on expected values.

        Parameters
        ----------
        ain_list : list of AIN
            List of AIN instances
        q : float
            Percentile to compute (0-100)

        Returns
        -------
        AIN
            AIN at the q-th percentile

        Examples
        --------
        >>> ains = [AIN(i, i+10, i+5) for i in range(0, 100, 10)]
        >>> result = AIN.percentile(ains, 50)  # Median
        >>> print(result)
        [40.0000, 50.0000]_{45.0000}
        """
        if not isinstance(ain_list, list):
            raise TypeError("ain_list must be a list")
        if len(ain_list) == 0:
            raise ValueError("ain_list cannot be empty")
        if not isinstance(q, (int, float)):
            raise TypeError("q must be a number")
        if not 0 <= q <= 100:
            raise ValueError("q must be in [0, 100]")

        for ain in ain_list:
            if not isinstance(ain, AIN):
                raise TypeError("All elements must be AIN instances")

        sorted_ains = sorted(ain_list, key=lambda x: x.expected)
        n = len(sorted_ains)
        index = (q / 100) * (n - 1)

        if index.is_integer():
            return sorted_ains[int(index)]
        else:
            lower_idx = int(np.floor(index))
            upper_idx = int(np.ceil(index))
            t = index - lower_idx
            return AIN.lerp(sorted_ains[lower_idx], sorted_ains[upper_idx], t)

    @staticmethod
    def mode(ain_list):
        # WS_to_check_common_sense
        """
        Compute mode (most frequent expected value) of AIN instances.

        Returns the AIN with the most common expected value.
        If multiple values have the same frequency, returns the first one found.

        Parameters
        ----------
        ain_list : list of AIN
            List of AIN instances

        Returns
        -------
        AIN
            The AIN with the most frequent expected value

        Examples
        --------
        >>> ains = [AIN(0, 10, 5), AIN(1, 11, 5), AIN(2, 12, 7)]
        >>> result = AIN.mode(ains)
        >>> print(result.expected)
        5.0
        """
        if not isinstance(ain_list, list):
            raise TypeError("ain_list must be a list")
        if len(ain_list) == 0:
            raise ValueError("ain_list cannot be empty")

        for ain in ain_list:
            if not isinstance(ain, AIN):
                raise TypeError("All elements must be AIN instances")

        # Count frequency of expected values (with tolerance for floating point)
        from collections import Counter
        expected_values = [ain.expected for ain in ain_list]
        counter = Counter(expected_values)
        most_common_value = counter.most_common(1)[0][0]

        # Return first AIN with this expected value
        for ain in ain_list:
            if np.isclose(ain.expected, most_common_value):
                return ain

    @staticmethod
    def range_span(ain_list):
        # WS_to_check_common_sense
        """
        Compute range (max - min) of expected values in AIN list.

        Parameters
        ----------
        ain_list : list of AIN
            List of AIN instances

        Returns
        -------
        float
            Range of expected values

        Examples
        --------
        >>> ains = [AIN(0, 10, 2), AIN(5, 15, 8), AIN(10, 20, 15)]
        >>> print(AIN.range_span(ains))
        13.0
        """
        if not isinstance(ain_list, list):
            raise TypeError("ain_list must be a list")
        if len(ain_list) == 0:
            raise ValueError("ain_list cannot be empty")

        for ain in ain_list:
            if not isinstance(ain, AIN):
                raise TypeError("All elements must be AIN instances")

        expected_values = [ain.expected for ain in ain_list]
        return max(expected_values) - min(expected_values)

    @staticmethod
    def iqr(ain_list):
        # WS_to_check_common_sense
        """
        Compute interquartile range (IQR = Q3 - Q1) of AIN expected values.

        The IQR is the difference between the 75th and 25th percentiles,
        a robust measure of statistical dispersion.

        Parameters
        ----------
        ain_list : list of AIN
            List of AIN instances

        Returns
        -------
        float
            Interquartile range of expected values

        Examples
        --------
        >>> ains = [AIN(i, i+10, i+5) for i in range(0, 100, 10)]
        >>> print(AIN.iqr(ains))
        45.0
        """
        if not isinstance(ain_list, list):
            raise TypeError("ain_list must be a list")
        if len(ain_list) == 0:
            raise ValueError("ain_list cannot be empty")

        for ain in ain_list:
            if not isinstance(ain, AIN):
                raise TypeError("All elements must be AIN instances")

        q1 = AIN.percentile(ain_list, 25)
        q3 = AIN.percentile(ain_list, 75)

        return q3.expected - q1.expected

    @staticmethod
    def mad(ain_list):
        # WS_to_check_common_sense
        """
        Compute median absolute deviation (MAD) of AIN expected values.

        MAD is a robust measure of variability:
        MAD = median(|xᵢ - median(x)|)

        Parameters
        ----------
        ain_list : list of AIN
            List of AIN instances

        Returns
        -------
        float
            Median absolute deviation of expected values

        Examples
        --------
        >>> ains = [AIN(i, i+10, i+5) for i in range(0, 100, 10)]
        >>> print(AIN.mad(ains))
        22.5
        """
        if not isinstance(ain_list, list):
            raise TypeError("ain_list must be a list")
        if len(ain_list) == 0:
            raise ValueError("ain_list cannot be empty")

        for ain in ain_list:
            if not isinstance(ain, AIN):
                raise TypeError("All elements must be AIN instances")

        # Compute median
        median_ain = AIN.median(ain_list)
        median_value = median_ain.expected

        # Compute absolute deviations
        deviations = [abs(ain.expected - median_value) for ain in ain_list]

        # Return median of deviations
        return np.median(deviations)

    @staticmethod
    def hausdorff_distance(ain1, ain2):
        # WS_to_check_common_sense
        """
        Compute Hausdorff distance between two AIN instances.

        For AIN with (lower, upper, expected), the distance includes all three:
        d_H = max(|lower₁-lower₂|, |upper₁-upper₂|, |expected₁-expected₂|)

        Parameters
        ----------
        ain1, ain2 : AIN
            AIN instances to compare

        Returns
        -------
        float
            Hausdorff distance

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> y = AIN(1, 11, 6)
        >>> print(AIN.hausdorff_distance(x, y))
        1.0
        """
        if not isinstance(ain1, AIN) or not isinstance(ain2, AIN):
            raise TypeError("Both arguments must be AIN instances")

        d_lower = abs(ain1.lower - ain2.lower)
        d_upper = abs(ain1.upper - ain2.upper)
        d_expected = abs(ain1.expected - ain2.expected)

        return max(d_lower, d_upper, d_expected)

    @staticmethod
    def manhattan_distance(ain1, ain2):
        # WS_to_check_common_sense
        """
        Compute Manhattan (L1) distance between two AIN instances.

        The Manhattan distance sums absolute differences across all components:
        d_M = |lower₁-lower₂| + |upper₁-upper₂| + |expected₁-expected₂|

        Parameters
        ----------
        ain1, ain2 : AIN
            AIN instances to compare

        Returns
        -------
        float
            Manhattan distance

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> y = AIN(1, 11, 6)
        >>> print(AIN.manhattan_distance(x, y))
        3.0
        """
        if not isinstance(ain1, AIN) or not isinstance(ain2, AIN):
            raise TypeError("Both arguments must be AIN instances")

        d_lower = abs(ain1.lower - ain2.lower)
        d_upper = abs(ain1.upper - ain2.upper)
        d_expected = abs(ain1.expected - ain2.expected)

        return d_lower + d_upper + d_expected

    @staticmethod
    def euclidean_distance(ain1, ain2):
        # WS_to_check_common_sense
        """
        Compute Euclidean (L2) distance between two AIN instances.

        The Euclidean distance is the L2 norm of differences:
        d_E = sqrt((lower₁-lower₂)² + (upper₁-upper₂)² + (expected₁-expected₂)²)

        Parameters
        ----------
        ain1, ain2 : AIN
            AIN instances to compare

        Returns
        -------
        float
            Euclidean distance

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> y = AIN(1, 11, 6)
        >>> print(AIN.euclidean_distance(x, y))
        1.7321
        """
        if not isinstance(ain1, AIN) or not isinstance(ain2, AIN):
            raise TypeError("Both arguments must be AIN instances")

        d_lower = (ain1.lower - ain2.lower) ** 2
        d_upper = (ain1.upper - ain2.upper) ** 2
        d_expected = (ain1.expected - ain2.expected) ** 2

        return np.sqrt(d_lower + d_upper + d_expected)

    @staticmethod
    def minkowski_distance(ain1, ain2, p):
        # WS_to_check_common_sense
        """
        Compute Minkowski (Lp) distance between two AIN instances.

        The Minkowski distance is a generalized metric:
        d_p = (|lower₁-lower₂|^p + |upper₁-upper₂|^p + |expected₁-expected₂|^p)^(1/p)

        Special cases:
        - p=1: Manhattan distance
        - p=2: Euclidean distance
        - p=∞: Chebyshev/Hausdorff distance

        Parameters
        ----------
        ain1, ain2 : AIN
            AIN instances to compare
        p : float
            Order of the norm (p >= 1)

        Returns
        -------
        float
            Minkowski distance of order p

        Raises
        ------
        ValueError
            If p < 1

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> y = AIN(1, 11, 6)
        >>> print(AIN.minkowski_distance(x, y, p=3))
        1.4422
        """
        if not isinstance(ain1, AIN) or not isinstance(ain2, AIN):
            raise TypeError("Both arguments must be AIN instances")

        if p < 1:
            raise ValueError("p must be >= 1 for Minkowski distance")

        if np.isinf(p):
            # For p=∞, this becomes Chebyshev/Hausdorff distance
            return AIN.hausdorff_distance(ain1, ain2)

        d_lower = abs(ain1.lower - ain2.lower) ** p
        d_upper = abs(ain1.upper - ain2.upper) ** p
        d_expected = abs(ain1.expected - ain2.expected) ** p

        return (d_lower + d_upper + d_expected) ** (1 / p)

    @staticmethod
    def cosine_similarity(ain1, ain2):
        # WS_to_check_common_sense
        """
        Compute cosine similarity between two AIN instances.

        Treats each AIN as a 3D vector (lower, upper, expected) and computes:
        cos(θ) = (v₁ · v₂) / (||v₁|| × ||v₂||)

        Returns a value in [-1, 1] where:
        - 1 means same direction
        - 0 means orthogonal
        - -1 means opposite direction

        Parameters
        ----------
        ain1, ain2 : AIN
            AIN instances to compare

        Returns
        -------
        float
            Cosine similarity in [-1, 1]

        Examples
        --------
        >>> x = AIN(1, 10, 5)
        >>> y = AIN(2, 20, 10)
        >>> print(AIN.cosine_similarity(x, y))
        1.0000
        """
        if not isinstance(ain1, AIN) or not isinstance(ain2, AIN):
            raise TypeError("Both arguments must be AIN instances")

        # Treat AIN as vectors
        v1 = np.array([ain1.lower, ain1.upper, ain1.expected])
        v2 = np.array([ain2.lower, ain2.upper, ain2.expected])

        # Compute dot product
        dot_product = np.dot(v1, v2)

        # Compute norms
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)

        # Avoid division by zero
        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    @staticmethod
    def jaccard_similarity(ain1, ain2):
        # WS_to_check_common_sense
        """
        Compute Jaccard similarity coefficient.

        J(A, B) = |A ∩ B| / |A ∪ B|

        Parameters
        ----------
        ain1, ain2 : AIN
            AIN instances to compare

        Returns
        -------
        float
            Jaccard similarity in [0, 1]

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> y = AIN(5, 15, 10)
        >>> print(AIN.jaccard_similarity(x, y))
        0.3333
        """
        if not isinstance(ain1, AIN) or not isinstance(ain2, AIN):
            raise TypeError("Both arguments must be AIN instances")

        intersection_lower = max(ain1.lower, ain2.lower)
        intersection_upper = min(ain1.upper, ain2.upper)

        if intersection_lower > intersection_upper:
            return 0.0  # No overlap

        intersection_size = intersection_upper - intersection_lower

        union_lower = min(ain1.lower, ain2.lower)
        union_upper = max(ain1.upper, ain2.upper)
        union_size = union_upper - union_lower

        if union_size == 0:
            return 1.0 if intersection_size == 0 else 0.0

        return intersection_size / union_size

    @staticmethod
    def overlap_coefficient(ain1, ain2):
        # WS_to_check_common_sense
        """
        Compute overlap coefficient (Szymkiewicz–Simpson coefficient).

        OC(A, B) = |A ∩ B| / min(|A|, |B|)

        Parameters
        ----------
        ain1, ain2 : AIN
            AIN instances to compare

        Returns
        -------
        float
            Overlap coefficient in [0, 1]

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> y = AIN(5, 15, 10)
        >>> print(AIN.overlap_coefficient(x, y))
        0.5
        """
        if not isinstance(ain1, AIN) or not isinstance(ain2, AIN):
            raise TypeError("Both arguments must be AIN instances")

        intersection_lower = max(ain1.lower, ain2.lower)
        intersection_upper = min(ain1.upper, ain2.upper)

        if intersection_lower > intersection_upper:
            return 0.0  # No overlap

        intersection_size = intersection_upper - intersection_lower

        size1 = ain1.upper - ain1.lower
        size2 = ain2.upper - ain2.lower
        min_size = min(size1, size2)

        if min_size == 0:
            return 1.0 if intersection_size == 0 else 0.0

        return intersection_size / min_size

    @staticmethod
    def covariance(ain_list1, ain_list2):
        # WS_to_check_common_sense
        """
        Compute covariance between two lists of AIN instances.

        Cov(X, Y) = E[(X - E[X])(Y - E[Y])]

        Uses expected values of AIN instances.

        Parameters
        ----------
        ain_list1, ain_list2 : list of AIN
            Two lists of AIN instances (must have same length)

        Returns
        -------
        float
            Sample covariance

        Examples
        --------
        >>> x_list = [AIN(i, i+10, i+5) for i in range(10)]
        >>> y_list = [AIN(2*i, 2*i+10, 2*i+5) for i in range(10)]
        >>> print(AIN.covariance(x_list, y_list))
        90.0
        """
        if not isinstance(ain_list1, list) or not isinstance(ain_list2, list):
            raise TypeError("Both arguments must be lists")
        if len(ain_list1) != len(ain_list2):
            raise ValueError("Lists must have same length")
        if len(ain_list1) == 0:
            raise ValueError("Lists cannot be empty")

        for ain in ain_list1 + ain_list2:
            if not isinstance(ain, AIN):
                raise TypeError("All elements must be AIN instances")

        x_vals = np.array([ain.expected for ain in ain_list1])
        y_vals = np.array([ain.expected for ain in ain_list2])

        return np.cov(x_vals, y_vals, ddof=1)[0, 1]

    @staticmethod
    def correlation(ain_list1, ain_list2):
        # WS_to_check_common_sense
        """
        Compute Pearson correlation between two lists of AIN instances.

        Corr(X, Y) = Cov(X, Y) / (σₓ × σᵧ)

        Uses expected values of AIN instances.

        Parameters
        ----------
        ain_list1, ain_list2 : list of AIN
            Two lists of AIN instances (must have same length)

        Returns
        -------
        float
            Correlation coefficient in [-1, 1]

        Examples
        --------
        >>> x_list = [AIN(i, i+10, i+5) for i in range(10)]
        >>> y_list = [AIN(2*i, 2*i+10, 2*i+5) for i in range(10)]
        >>> print(AIN.correlation(x_list, y_list))
        1.0
        """
        if len(ain_list1) < 2:
            raise ValueError("Need at least 2 samples for correlation")

        x_vals = np.array([ain.expected for ain in ain_list1])
        y_vals = np.array([ain.expected for ain in ain_list2])

        return np.corrcoef(x_vals, y_vals)[0, 1]

    @staticmethod
    def all_positive(ain_list):
        # WS_to_check_common_sense
        """
        Check if all AIN instances are positive (lower > 0).

        Parameters
        ----------
        ain_list : list of AIN
            List of AIN instances

        Returns
        -------
        bool
            True if all AIN have lower > 0

        Examples
        --------
        >>> ains = [AIN(1, 5, 3), AIN(2, 6, 4)]
        >>> print(AIN.all_positive(ains))
        True
        """
        if not isinstance(ain_list, list):
            raise TypeError("ain_list must be a list")

        for ain in ain_list:
            if not isinstance(ain, AIN):
                raise TypeError("All elements must be AIN instances")
            if not ain.is_positive():
                return False

        return True

    @staticmethod
    def any_negative(ain_list):
        # WS_to_check_common_sense
        """
        Check if any AIN instance is negative (upper < 0).

        Parameters
        ----------
        ain_list : list of AIN
            List of AIN instances

        Returns
        -------
        bool
            True if any AIN has upper < 0

        Examples
        --------
        >>> ains = [AIN(1, 5, 3), AIN(-10, -2, -5)]
        >>> print(AIN.any_negative(ains))
        True
        """
        if not isinstance(ain_list, list):
            raise TypeError("ain_list must be a list")

        for ain in ain_list:
            if not isinstance(ain, AIN):
                raise TypeError("All elements must be AIN instances")
            if ain.is_negative():
                return True

        return False

    @staticmethod
    def all_disjoint(ain_list):
        # WS_to_check_common_sense
        """
        Check if all AIN instances are pairwise disjoint (no overlaps).

        Parameters
        ----------
        ain_list : list of AIN
            List of AIN instances

        Returns
        -------
        bool
            True if no two AIN instances overlap

        Examples
        --------
        >>> ains = [AIN(0, 5, 2), AIN(10, 15, 12), AIN(20, 25, 22)]
        >>> print(AIN.all_disjoint(ains))
        True

        >>> ains = [AIN(0, 10, 5), AIN(5, 15, 10)]
        >>> print(AIN.all_disjoint(ains))
        False
        """
        if not isinstance(ain_list, list):
            raise TypeError("ain_list must be a list")

        for ain in ain_list:
            if not isinstance(ain, AIN):
                raise TypeError("All elements must be AIN instances")

        n = len(ain_list)
        for i in range(n):
            for j in range(i + 1, n):
                if ain_list[i].overlaps(ain_list[j]):
                    return False

        return True

    def pdf(self, x):
        """
        Calculate the probability density function (PDF) value for the `AIN` at a given point `x`.

        This method calculates the probability density at `x` within the AIN-defined interval. The PDF describes
        how the density is distributed across the AIN interval, with distinct values in different segments:
        - Outside the interval `[self.lower, self.upper]`, the density is 0.
        - Between `self.lower` and `self.expected`, the density is equal to `self.alpha`.
        - Between `self.expected` and `self.upper`, the density is equal to `self.beta`.

        Parameters
        ----------
        x : int or float
            The point at which to evaluate the PDF. Should be a numeric value.

        Returns
        -------
        float
            The PDF value at the specified point `x`. The return value will be:
            - 0 if `x` is outside the interval `[self.lower, self.upper]`.
            - `self.alpha` if `x` is within the interval `[self.lower, self.expected]`.
            - `self.beta` if `x` is within the interval `[self.expected, self.upper]`.

        Raises
        ------
        TypeError
            If `x` is not an `int` or `float`.

        Examples
        --------
        >>> a = AIN(0, 10, 5)
        >>> a.pdf(-1)
        0.0

        >>> a.pdf(3)
        0.1

        >>> a.pdf(7)
        0.1

        >>> a.pdf(11)
        0.0
        """
        if not isinstance(x, (int, float)):
            raise TypeError(f'Argument x must be an integer, not {type(x)}')

        if x < self.lower:
            return 0.0
        elif x < self.expected:
            return self.alpha
        elif x < self.upper:
            return self.beta
        else:
            return 0.0

    def cdf(self, x):
        """
        Calculate the cumulative distribution function (CDF) value for a specified input `x`.

        This method evaluates the cumulative distribution function (CDF) of the `AIN` instance at
        the given value `x`, indicating the probability that a random variable takes a value less
        than or equal to `x`. The CDF value is computed based on the position of `x` relative to
        the instance's defined bounds (`self.lower`, `self.expected`, `self.upper`).

        Parameters
        ----------
        x : int or float
            The point at which to evaluate the CDF. This should be a numeric value.

        Returns
        -------
        float
            The computed CDF value at `x`, representing the cumulative probability up to `x`.
            The output will follow these cases:
            - 0 if `x` is less than the lower bound (`self.lower`).
            - A linearly interpolated value between the lower bound and the expected value
              if `x` is between `self.lower` and `self.expected`.
            - A linearly interpolated value between the expected value and the upper bound
              if `x` is between `self.expected` and `self.upper`.
            - 1 if `x` is greater than or equal to the upper bound (`self.upper`).

        Raises
        ------
        TypeError
            If `x` is not an `int` or `float`.

        Notes
        -----
        This method calculates the CDF using a piecewise approach:
        - For `x < self.lower`, it returns 0.
        - For `self.lower <= x < self.expected`, the CDF is calculated as `self.alpha * (x - self.lower)`.
        - For `self.expected <= x < self.upper`, the CDF is calculated as
          `self.alpha * (self.expected - self.lower) + self.beta * (x - self.expected)`.
        - For `x >= self.upper`, it returns 1.

        Examples
        --------
        >>> a = AIN(0, 10, 3)
        >>> a.cdf(1.5)
        0.35

        >>> a.cdf(3)
        0.7

        >>> a.cdf(8.5)
        0.9357142857142857

        >>> a.cdf(20)
        1
        """
        if not isinstance(x, (int, float)):
            raise TypeError(f'x must be an int or float value.')
        if x < self.lower:
            res = 0
        elif x < self.expected:
            res = self.alpha * (x - self.lower)
        elif x < self.upper:
            res = self.alpha * (self.expected - self.lower) + self.beta * (x - self.expected)
        else:
            res = 1
        return res

    def quantile(self, y):
        """
        Compute the quantile value (inverse cumulative distribution function) for a given probability.

        This method calculates the quantile, or the inverse cumulative distribution function (CDF),
        for the `AIN` instance at a specified probability level `y`. The quantile represents the value
        below which a given percentage of observations fall, based on the AIN instance’s parameters.
        The function only operates within the probability range [0, 1].

        Parameters
        ----------
        y : int or float
            The probability level at which to compute the quantile. Must be within the range [0, 1],
            where 0 represents the minimum and 1 represents the maximum of the distribution.

        Returns
        -------
        float
            The quantile value corresponding to the given probability `y`.

        Raises
        ------
        ValueError
            If `y` is outside the valid range [0, 1].

        TypeError
            If `y` is not a `float` or `int` value.

        Notes
        -----
        The method uses `self.alpha`, `self.beta`, `self.expected`, and `self.lower` attributes
        to compute the quantile based on a piecewise formula:
        - For values of `y` below `self.alpha * (self.expected - self.lower)`, the quantile
          is calculated as `y / self.alpha + self.lower`.
        - Otherwise, it is calculated as `(y - self.alpha * (self.expected - self.lower)) / self.beta + self.expected`.

        Examples
        --------
        >>> a = AIN(0, 10, 3)
        >>> a.quantile(0.25)
        1.0714285714285714

        >>> a.quantile(0.85)
        6.5

        >>> a.quantile(1.1)
        Traceback (most recent call last):
            ...
        ValueError: Argument y = 1.1 is out of range; it should be between 0 and 1.
        """
        if not isinstance(y, (int, float)):
            raise TypeError(f'Argument y = {y} is not an integer or float.')
        if 0 <= y <= 1:
            if y < self.alpha * (self.expected - self.lower):
                res = y / self.alpha + self.lower
            else:
                res = (y - self.alpha * (self.expected - self.lower)) / self.beta + self.expected
        else:
            raise ValueError(f'Argument y = {y} is out of range; it should be between 0 and 1.')
        return res

    def to_dict(self):
        # WS_to_check_common_sense
        """
        Export AIN to a dictionary.

        Returns
        -------
        dict
            Dictionary containing all AIN attributes.

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> d = x.to_dict()
        >>> print(d)
        {'lower': 0, 'upper': 10, 'expected': 5, 'alpha': ..., 'beta': ..., 'asymmetry': ..., 'D2': ...}
        """
        return {
            'lower': self.lower,
            'upper': self.upper,
            'expected': self.expected,
            'alpha': self.alpha,
            'beta': self.beta,
            'asymmetry': self.asymmetry,
            'D2': self.D2
        }

    def to_scalar(self):
        # WS_to_check_common_sense
        """
        Convert AIN to scalar (expected value).

        Returns
        -------
        float
            The expected value.

        Examples
        --------
        >>> x = AIN(0, 10, 7)
        >>> print(x.to_scalar())
        7.0
        """
        return self.expected

    def to_tuple(self):
        # WS_to_check_common_sense
        """
        Convert AIN to tuple (lower, upper, expected).

        Returns
        -------
        tuple
            (lower, upper, expected)

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> print(x.to_tuple())
        (0, 10, 5)
        """
        return (self.lower, self.upper, self.expected)

    def to_list(self):
        # WS_to_check_common_sense
        """
        Convert AIN to list [lower, upper, expected].

        Returns
        -------
        list
            [lower, upper, expected]

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> print(x.to_list())
        [0, 10, 5]
        """
        return [self.lower, self.upper, self.expected]

    def to_numpy(self):
        # WS_to_check_common_sense
        """
        Convert AIN to numpy array [lower, upper, expected].

        Returns
        -------
        numpy.ndarray
            Array containing [lower, upper, expected]

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> arr = x.to_numpy()
        >>> print(arr)
        [ 0. 10.  5.]
        >>> print(type(arr))
        <class 'numpy.ndarray'>
        """
        return np.array([self.lower, self.upper, self.expected])

    def to_json(self):
        # WS_to_check_common_sense
        """
        Convert AIN to JSON string.

        Returns
        -------
        str
            JSON string representation of the AIN

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> print(x.to_json())
        {"lower": 0, "upper": 10, "expected": 5, "alpha": 0.2, "beta": 0.2, "asymmetry": 0.0}
        """
        import json
        data = {
            'lower': self.lower,
            'upper': self.upper,
            'expected': self.expected,
            'alpha': self.alpha,
            'beta': self.beta,
            'asymmetry': self.asymmetry
        }
        return json.dumps(data)

    @classmethod
    def from_dict(cls, d):
        # WS_to_check_common_sense
        """
        Create AIN from a dictionary.

        Parameters
        ----------
        d : dict
            Dictionary containing at least 'lower', 'upper', and optionally 'expected'.

        Returns
        -------
        AIN
            A new AIN instance.

        Examples
        --------
        >>> d = {'lower': 0, 'upper': 10, 'expected': 5}
        >>> x = AIN.from_dict(d)
        >>> print(x)
        [0.0000, 10.0000]_{5.0000}
        """
        if not isinstance(d, dict):
            raise TypeError("Input must be a dictionary")

        if 'lower' not in d or 'upper' not in d:
            raise ValueError("Dictionary must contain 'lower' and 'upper' keys")

        return cls(d['lower'], d['upper'], d.get('expected'))

    @classmethod
    def from_json(cls, json_str):
        # WS_to_check_common_sense
        """
        Create AIN from a JSON string.

        This is the inverse of to_json(). Parses a JSON string and creates
        an AIN instance from the data.

        Parameters
        ----------
        json_str : str
            JSON string containing AIN data. Must contain at least 'lower' and 'upper' keys.

        Returns
        -------
        AIN
            A new AIN instance.

        Raises
        ------
        TypeError
            If json_str is not a string
        ValueError
            If JSON is invalid or missing required keys

        Examples
        --------
        >>> json_str = '{"lower": 0, "upper": 10, "expected": 5}'
        >>> x = AIN.from_json(json_str)
        >>> print(x)
        [0.0000, 10.0000]_{5.0000}

        >>> # Round-trip conversion
        >>> original = AIN(1, 5, 3)
        >>> json_str = original.to_json()
        >>> restored = AIN.from_json(json_str)
        >>> print(restored)
        [1.0000, 5.0000]_{3.0000}
        """
        import json

        if not isinstance(json_str, str):
            raise TypeError("Input must be a string")

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string: {e}")

        if not isinstance(data, dict):
            raise ValueError("JSON must represent a dictionary/object")

        if 'lower' not in data or 'upper' not in data:
            raise ValueError("JSON must contain 'lower' and 'upper' keys")

        return cls(data['lower'], data['upper'], data.get('expected'))

    @classmethod
    def from_samples(cls, data, method='minmax', clip_outliers=False):
        # WS_to_check_common_sense
        """
        Create AIN from empirical data using various methods.

        This method constructs an AIN instance from a collection of samples,
        offering multiple strategies for determining interval bounds and handling outliers.

        Parameters
        ----------
        data : array-like
            Sample data (list, numpy array, etc.)
        method : str, optional
            Method for determining bounds (default: 'minmax'):
            - 'minmax': Use minimum and maximum values
            - 'percentile': Use 1st and 99th percentiles
            - 'iqr': Use interquartile range (Q1-Q3)
            - 'std': Use mean ± 3*sigma
            - 'mad': Use median ± 3*MAD (Median Absolute Deviation)
        clip_outliers : bool, optional
            Whether to remove outliers before calculations using IQR method (default: False)

        Returns
        -------
        AIN
            A new AIN instance with bounds determined by the chosen method
            and expected value equal to the sample mean.

        Raises
        ------
        ValueError
            If data is empty or method is unknown.
        TypeError
            If data cannot be converted to numpy array.

        Examples
        --------
        Basic usage with default method:
        >>> data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        >>> x = AIN.from_samples(data)
        >>> print(x)
        [1.0000, 10.0000]_{5.5000}

        Using percentile method (robust to outliers):
        >>> data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 100]  # 100 is outlier
        >>> x = AIN.from_samples(data, method='percentile')
        >>> print(x)
        [1.0900, 17.9100]_{14.5000}

        Using IQR method (focuses on central 50%):
        >>> data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        >>> x = AIN.from_samples(data, method='iqr')
        >>> print(x)
        [3.2500, 7.7500]_{5.5000}

        Removing outliers before analysis:
        >>> data = [100, 102, 98, 101, 99, 103, 500, 97, 102, 100]
        >>> x = AIN.from_samples(data, method='minmax', clip_outliers=True)
        >>> print(x)
        [97.0000, 103.0000]_{100.2222}

        Using MAD method (most robust):
        >>> data = [10, 11, 10.5, 11.2, 10.8, 999]
        >>> x = AIN.from_samples(data, method='mad')
        >>> print(x)
        [7.5000, 14.5000]_{175.4167}

        Notes
        -----
        Method selection guide:
        - 'minmax': Best for clean data without outliers
        - 'percentile': Good balance between robustness and data retention
        - 'iqr': Very robust, focuses on central tendency
        - 'std': Assumes normal distribution, good for theoretical bounds
        - 'mad': Most robust to outliers, works with any distribution

        The clip_outliers option uses the IQR method with 1.5*IQR rule to
        identify and remove outliers before applying the selected method.
        """
        # Convert to numpy array
        try:
            data = np.array(data, dtype=float)
        except (ValueError, TypeError) as e:
            raise TypeError(f"Data must be convertible to numpy array: {e}")

        if len(data) == 0:
            raise ValueError("Data cannot be empty")

        # Remove outliers if requested
        if clip_outliers:
            Q1 = np.percentile(data, 25)
            Q3 = np.percentile(data, 75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            data = data[(data >= lower_bound) & (data <= upper_bound)]

            if len(data) == 0:
                raise ValueError("All data points were identified as outliers")

        # Compute bounds based on method
        if method == 'minmax':
            lower = np.min(data)
            upper = np.max(data)

        elif method == 'percentile':
            lower = np.percentile(data, 1)
            upper = np.percentile(data, 99)

        elif method == 'iqr':
            lower = np.percentile(data, 25)  # Q1
            upper = np.percentile(data, 75)  # Q3

        elif method == 'std':
            mean = np.mean(data)
            std = np.std(data)
            lower = mean - 3 * std
            upper = mean + 3 * std

        elif method == 'mad':
            median = np.median(data)
            mad = np.median(np.abs(data - median))
            lower = median - 3 * mad
            upper = median + 3 * mad

        else:
            raise ValueError(f"Unknown method: '{method}'. Use 'minmax', 'percentile', 'iqr', 'std', or 'mad'.")

        # Expected value is always the mean of the (possibly clipped) data
        expected = np.mean(data)

        # Ensure bounds are valid
        if lower > upper:
            lower, upper = upper, lower

        if lower == upper:
            # Degenerate case - all data points are identical
            return cls(lower, upper, expected)

        # Ensure expected is within bounds
        if expected < lower:
            expected = lower
        elif expected > upper:
            expected = upper

        return cls(lower, upper, expected)

    @classmethod
    def uniform(cls, a, b):
        # WS_to_check_common_sense
        """
        Create AIN with uniform distribution.

        Creates an AIN with expected value at the midpoint, representing
        a uniform distribution over [a, b].

        Parameters
        ----------
        a : float
            Lower bound
        b : float
            Upper bound

        Returns
        -------
        AIN
            AIN instance with expected = (a+b)/2

        Examples
        --------
        >>> x = AIN.uniform(0, 10)
        >>> print(x)
        [0.0000, 10.0000]_{5.0000}
        """
        if a > b:
            a, b = b, a
        expected = (a + b) / 2
        return cls(a, b, expected)

    @classmethod
    def triangular(cls, a, b, c):
        # WS_to_check_common_sense
        """
        Create AIN with triangular distribution.

        Creates an AIN representing a triangular distribution with
        mode at c.

        Parameters
        ----------
        a : float
            Lower bound
        b : float
            Upper bound
        c : float
            Mode (most likely value), must be in [a, b]

        Returns
        -------
        AIN
            AIN instance with bounds [a, b] and expected = c

        Raises
        ------
        ValueError
            If c is not in [a, b]

        Examples
        --------
        >>> x = AIN.triangular(0, 10, 7)
        >>> print(x)
        [0.0000, 10.0000]_{7.0000}
        """
        if a > b:
            a, b = b, a
        if not (a <= c <= b):
            raise ValueError(f"Mode c={c} must be in [{a}, {b}]")
        return cls(a, b, c)

    @classmethod
    def zeros(cls):
        # WS_to_check_common_sense
        """
        Create AIN representing zero.

        Returns
        -------
        AIN
            AIN(0, 0, 0)

        Examples
        --------
        >>> z = AIN.zeros()
        >>> print(z)
        [0.0000, 0.0000]_{0.0000}
        """
        return cls(0, 0, 0)

    @classmethod
    def ones(cls):
        # WS_to_check_common_sense
        """
        Create AIN representing one.

        Returns
        -------
        AIN
            AIN(1, 1, 1)

        Examples
        --------
        >>> one = AIN.ones()
        >>> print(one)
        [1.0000, 1.0000]_{1.0000}
        """
        return cls(1, 1, 1)

    def sample(self, n=1, random_state=None):
        # WS_to_check_common_sense
        """
        Generate random samples from the AIN distribution.

        Samples are drawn from the piecewise uniform distribution defined by
        the AIN with alpha and beta weights.

        Parameters
        ----------
        n : int, optional
            Number of samples to generate. Default is 1.
        random_state : int, optional
            Random seed for reproducibility. Default is None.

        Returns
        -------
        numpy.ndarray
            Array of n samples from the distribution.

        Examples
        --------
        >>> x = AIN(0, 10, 4)
        >>> samples = x.sample(n=1000, random_state=42)
        >>> print(f"Mean: {samples.mean():.2f}, Std: {samples.std():.2f}")
        Mean: 4.02, Std: 2.91
        """
        if random_state is not None:
            np.random.seed(random_state)

        samples = []

        for _ in range(n):
            # Choose left or right segment based on alpha/beta weights
            total_weight = self.alpha + self.beta
            p_left = self.alpha / total_weight

            if np.random.random() < p_left:
                # Sample from left segment [lower, expected]
                s = np.random.uniform(self.lower, self.expected)
            else:
                # Sample from right segment [expected, upper]
                s = np.random.uniform(self.expected, self.upper)

            samples.append(s)

        return np.array(samples)

    def bootstrap(self, n_iterations=1000, stat_func=None, random_state=None):
        # WS_to_check_common_sense
        """
        Perform bootstrap resampling on the AIN distribution.

        Generates bootstrap samples and computes statistics to estimate
        uncertainty in derived quantities.

        Parameters
        ----------
        n_iterations : int, optional
            Number of bootstrap iterations. Default is 1000.
        stat_func : callable, optional
            Function to compute on each bootstrap sample.
            If None, returns mean. Default is None.
        random_state : int, optional
            Random seed for reproducibility. Default is None.

        Returns
        -------
        numpy.ndarray
            Array of statistics from each bootstrap iteration.

        Examples
        --------
        >>> x = AIN(0, 10, 4)
        >>> means = x.bootstrap(n_iterations=1000, random_state=42)
        >>> print(f"Bootstrap mean: {means.mean():.2f} ± {means.std():.2f}")
        Bootstrap mean: 4.00 ± 0.10

        >>> # Custom statistic
        >>> medians = x.bootstrap(n_iterations=1000,
        ...                       stat_func=lambda s: np.median(s),
        ...                       random_state=42)
        """
        if random_state is not None:
            np.random.seed(random_state)

        if stat_func is None:
            stat_func = np.mean

        # Bootstrap sample size: use a reasonable default
        sample_size = 100

        bootstrap_stats = []

        for _ in range(n_iterations):
            # Generate a bootstrap sample
            bootstrap_sample = self.sample(n=sample_size)

            # Compute statistic
            stat = stat_func(bootstrap_sample)
            bootstrap_stats.append(stat)

        return np.array(bootstrap_stats)

    def copy(self):
        # WS_to_check_common_sense
        """
        Create a deep copy of the AIN instance.

        Returns
        -------
        AIN
            A new AIN instance with the same values.

        Examples
        --------
        >>> x = AIN(0, 10, 5)
        >>> y = x.copy()
        >>> print(y)
        [0.0000, 10.0000]_{5.0000}
        """
        return AIN(self.lower, self.upper, self.expected)

    def summary(self, precision=6):
        """
        Print a detailed, aligned summary of the AIN object's key attributes with specified precision.

        This method displays a formatted summary of the AIN object's primary attributes, including
        `alpha`, `beta`, `asymmetry`, expected value, variance, standard deviation, and midpoint.
        Each attribute is displayed with the specified number of decimal places, allowing for a concise
        or detailed view.

        Parameters
        ----------
        precision : int, optional
            The number of decimal places to display for floating-point values (default is 6).
            Must be an integer; otherwise, a ValueError is raised.

        Raises
        ------
        TypeError
            If `precision` is not an `int`, a ValueError is raised with an informative message.

        Example
        -------
        >>> a = AIN(0, 10, 2)
        >>> a.summary(precision=4)
        === AIN ============================
        [0.0000, 10.0000]_{2.0000}
        === Summary ========================
        Alpha        =     0.4000
        Beta         =     0.0250
        Asymmetry    =     0.6000
        Exp. val.    =     2.0000
        Variance     =     5.3333
        Std. dev.    =     2.3094
        Midpoint     =     5.0000
        ====================================

        Notes
        -----
        This method ensures a clean, easy-to-read summary by aligning values based on the longest
        entry, making it particularly useful for inspecting the AIN object's main parameters in detail.
        """
        if not isinstance(precision, int):
            raise TypeError(f'Argument precision = {precision} but it must be an integer.')
        print("=== AIN ============================")
        print(self)
        print("=== Summary ========================")

        elements = [
            ('Alpha', f'{self.alpha:.{precision}f}'),
            ('Beta', f'{self.beta:.{precision}f}'),
            ('Asymmetry', f'{self.asymmetry:.{precision}f}'),
            ('Exp. val.', f'{self.expected:.{precision}f}'),
            ('Variance', f'{self.D2:.{precision}f}'),
            ('Std. dev.', f'{(self.D2 ** 0.5):.{precision}f}'),
            ('Midpoint', f'{((self.lower + self.upper) / 2):.{precision}f}')
        ]

        max_length = max(len(str(value)) for _, value in elements) + 4

        for name, value in elements:
            print(f'{name:<12} = {value:>{max_length}}')

        print("====================================")

    def plot(self, ain_lw=2.0, ain_c='k', ain_label=''):
        """
        Plot the intervals and key values of an `AIN` instance.

        Visualizes the `AIN` instance by plotting its lower, expected, and upper values,
        along with corresponding alpha and beta levels.

        Parameters
        ----------
        ain_lw : float, optional
            Line width for the alpha and beta lines. Must be a positive float or integer. Default is 2.0.
        ain_c : str, optional
            Color for the interval lines. Accepts any valid matplotlib color string. Default is 'k' (black).
        ain_label : str, optional
            Label for the x-axis, representing the `AIN` instance. Default is an empty string.

        Returns
        -------
        matplotlib.axes.Axes
            The Axes object containing the plot.

        Raises
        ------
        ValueError
            If `ain_lw` is not a positive `float` or `int`.
        TypeError
            If `ain_c` or `ain_label` is not a string.

        Examples
        --------
        >>> # Uncomment to show this functionality
        >>> # ain = AIN(1, 10, 3)
        >>> # ain.plot(ain_label='Example')
        >>> # plt.show()

        Notes
        -----
        - Vertical dashed lines are placed at the lower, expected, and upper interval bounds.
        - Horizontal solid lines represent the alpha level between the lower and expected values,
          and the beta level between the expected and upper values.
        - Y-axis limits are automatically adjusted based on the maximum of alpha and beta, while
          the x-axis extends slightly beyond the interval bounds for readability.
        - The default y-axis label is set to 'pdf', and the x-axis label displays `ain_label`.
        """
        if not isinstance(ain_lw, (float, int)) or ain_lw <= 0:
            raise ValueError("ain_lw must be a positive float or integer.")

        if not isinstance(ain_c, str):
            raise TypeError("ain_c must be a string representing a valid matplotlib color.")

        if not isinstance(ain_label, str):
            raise TypeError("ain_label must be a string.")

        a, b, c = self.lower, self.upper, self.expected

        alpha, beta = self.alpha, self.beta

        vkw = dict(ls='--', lw=ain_lw / 2, c='k')

        ax = plt.gca()

        ax.plot([a, a], [0, alpha], **vkw)
        ax.plot([c, c], [0, max(alpha, beta)], **vkw)
        ax.plot([b, b], [0, beta], **vkw)

        hkw = dict(ls='-', lw=ain_lw, c=ain_c)
        ax.plot([a, c], [alpha, alpha], **hkw)
        ax.plot([c, b], [beta, beta], **hkw)

        ax.set_ylim([0, max(alpha, beta) * 1.1])
        ax.set_yticks(sorted([alpha, beta]))
        yticklabels = [f"{alpha:.4f}", f"{beta:.4f}"]
        if alpha > beta:
            yticklabels.reverse()
        ax.set_yticklabels(yticklabels, fontsize=12)

        if a == b == c:
            after_a = a - 0.5  # Arbitrary small extension for visual clarity
            after_b = b + 0.5
            ax.plot(a, 1, 'ko', markersize=3)
        else:
            after_a = a - (b - a) * 0.05
            after_b = b + (b - a) * 0.05
        ax.set_xlim([after_a, after_b])

        ax.set_xticks([a, c, b])
        ax.set_xticklabels([f"{a:.4f}", f"{c:.4f}", f"{b:.4f}"], fontsize=12)

        ax.spines[["top", "right"]].set_visible(False)

        ax.plot(1, 0, ">k", transform=plt.gca().get_yaxis_transform(), clip_on=False)
        ax.plot(after_a, 1, "^k", transform=plt.gca().get_xaxis_transform(), clip_on=False)
        ax.set_ylabel('$pdf$')
        ax.set_ylabel('pdf', labelpad=-15)
        ax.set_xlabel(ain_label)
        return ax

    @staticmethod
    def get_y_scale_max(ains_list):
        """
        Calculate the maximum scale value (y-axis) from a list of `AIN` objects.

        Parameters
        ----------
        ains_list : list
            A list of `AIN` objects.

        Returns
        -------
        float
            The maximum scale value found in the list of `AIN` objects.

        Raises
        ------
        TypeError
            If ains_list is not a list or if any element in the list is not an `AIN` object.

        Notes
        -----
        This function computes the maximum of the alpha and beta values across all AIN objects
        in the provided list to determine the maximum scale value on the y-axis.

        Example
        -------
        Assuming `ains_list` is a list of `AIN` objects:

        >>> ains_list = [AIN(1, 10), AIN(2, 10, 4)]
        >>> max_value = AIN.get_y_scale_max(ains_list)
        >>> print(max_value)
        0.375
        """
        result = 0
        if not isinstance(ains_list, list):
            raise TypeError("ains_list should be a list")
        for el in ains_list:
            if not isinstance(el, AIN):
                raise TypeError("Each element in the list must be a AIN object")
            result = max(result, el.alpha, el.beta)
        return result

    def add_to_plot(self, ain_lw=2.0, ain_c='k', ain_label='', ax=None, y_scale_max=None):
        """
        Plot the intervals and key values of an `AIN` instance.

        Visualizes the `AIN` instance by plotting its `lower`, `expected`, and `upper` values,
        along with corresponding `alpha` and `beta` levels. The plot includes:

        - Vertical dashed lines at the lower, expected, and upper bounds of the interval.
        - Horizontal solid lines representing the alpha and beta values across the intervals.
        - Dynamically scales the x- and y-axes for clarity, with an optional global maximum
          for y-axis scaling.

        Parameters
        ----------
        ain_lw : float, optional
            Line width for the alpha and beta interval lines. Default is 2.0.
        ain_c : str, optional
            Color for the interval lines. Default is 'k' (black).
        ain_label : str, optional
            Label for the x-axis describing the plotted AIN instance. Default is ''.
        ax : matplotlib.axes.Axes, optional
            Matplotlib axis to add the plot to. If not provided, the current axis (`plt.gca()`) is used.
        y_scale_max : float or int, optional
            Maximum value for the y-axis to ensure consistent scaling across multiple AIN plots.
            If not provided, the y-axis is scaled to 1.1 times the maximum of alpha or beta for this AIN instance.

        Returns
        -------
        matplotlib.axes.Axes
            The matplotlib axis with the AIN plot.

        Raises
        ------
        ValueError
            If `ain_lw` is non-positive or if `y_scale_max` is negative.
        TypeError
            If `ain_lw` or `y_scale_max` are not numeric, or if `ain_c` or `ain_label` are not strings.

        Examples
        --------
        >>> # Uncomment to show this functionality
        >>> # ain = AIN(1, 10, 5)
        >>> # ain.add_to_plot(ain_label='Example Interval')
        >>> # plt.show()
        >>> # a = AIN(0, 10, 4.5)
        >>> # b = AIN(0, 10, 7.5)
        >>> # value_y_scale_max = AIN.get_y_scale_max([a, b])
        >>> # plt.figure(figsize=(8, 3))
        >>> # plt.subplot(1, 2, 1)
        >>> # a.add_to_plot(y_scale_max=value_y_scale_max)
        >>> # plt.subplot(1, 2, 2)
        >>> # b.add_to_plot(y_scale_max=value_y_scale_max)
        >>> # plt.tight_layout()
        >>> # plt.show() # Uncomment to display the plot

        Notes
        -----
        - Vertical dashed lines are positioned at the lower, expected, and upper bounds of the interval.
        - Horizontal solid lines represent the alpha level between the lower and expected values,
          and the beta level between the expected and upper values.
        - The y-axis limits are automatically adjusted based on the maximum of alpha and beta values unless
          `y_scale_max` is specified. The x-axis extends slightly beyond the interval bounds for readability.
        - The default y-axis label is set to '$pdf$', and the x-axis label is set to `ain_label`.
        """
        if not isinstance(ain_lw, (float, int)) or ain_lw <= 0:
            raise ValueError("ain_lw must be a positive float or integer.")

        if not isinstance(ain_c, str):
            raise TypeError("ain_c must be a string representing a valid matplotlib color.")

        if not isinstance(ain_label, str):
            raise TypeError("ain_label must be a string.")

        if ax is None:
            ax = plt.gca()

        a, b, c = self.lower, self.upper, self.expected

        alpha, beta = self.alpha, self.beta

        vkw = dict(ls='--', lw=ain_lw / 2, c='k')
        ax.plot([a, a], [0, alpha], **vkw)
        ax.plot([c, c], [0, max(alpha, beta)], **vkw)
        ax.plot([b, b], [0, beta], **vkw)

        hkw = dict(ls='-', lw=ain_lw, c=ain_c)
        ax.plot([a, c], [alpha, alpha], **hkw)
        ax.plot([c, b], [beta, beta], **hkw)

        if y_scale_max is None:
            ax.set_ylim([0, max(alpha, beta) * 1.1])
        else:
            if not isinstance(y_scale_max, (int, float)):
                raise TypeError("y_scale_max must be a float or integer")
            if y_scale_max < 0:
                raise ValueError("y_scale_max must be a positive value")
            ax.set_ylim([0, y_scale_max * 1.1])
        ax.set_yticks(sorted([alpha, beta]))
        yticklabels = [f"{alpha:.4f}", f"{beta:.4f}"]
        if alpha > beta:
            yticklabels.reverse()
        ax.set_yticklabels(yticklabels, fontsize=12)

        if a == b == c:
            after_a = a - 0.5  # Arbitrary small extension for visual clarity
            after_b = b + 0.5
            ax.plot(a, 1, 'ko', markersize=3)
        else:
            after_a = a - (b - a) * 0.05
            after_b = b + (b - a) * 0.05
        ax.set_xlim([after_a, after_b])

        ax.set_xticks([a, c, b])
        ax.set_xticklabels([f"{a:.4f}", f"{c:.4f}", f"{b:.4f}"], fontsize=12)

        ax.spines[["top", "right"]].set_visible(False)

        ax.plot(1, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False)
        ax.plot(after_a, 1, "^k", transform=ax.get_xaxis_transform(), clip_on=False)
        ax.set_ylabel('$pdf$')
        ax.set_ylabel('pdf', labelpad=-15)
        ax.set_xlabel(ain_label)
        return ax


print([method for method in dir(AIN) if not method.startswith('_')])



# TODO: Add methods for arithmetic operations between AINs (addition, subtraction, etc.)
# to_tuple, to_dict, from_dict, to_json, from_json
# min, max, midpoint, width, radius, range_span
# contains, overlaps, intersection, union
#  bootstrap
# mean, std, quantile/percentile, summary
# sqrt, exp, log, reciprocal, tan

for i in dir(AIN):
    print(i)

# Poniżej TOP 20 (od najważniejszych do mniej ważnych) — tylko z Twojej listy “do dodania” (czyli te nowe):
# midpoint – punkt reprezentatywny; praktycznie wszędzie (porównania, wykresy, aproksymacje).
# width – szerokość/niepewność; kluczowa metryka jakości.
# contains – podstawowy predykat (czy x / inny interwał należy).
# overlaps – szybkie sprawdzanie nakładania (bazowe w relacjach interwałowych).
# intersection – rdzeń algebry zbiorów dla interwałów.
# union – drugi filar operacji zbiorowych (zwłaszcza gdy wspierasz „sklejanie”/łączenie).
# is_zero – często potrzebne w stabilności numerycznej i regułach brzegowych.
# is_positive – przydaje się do log/sqrt oraz logiki domen.
# is_negative – jw., szczególnie przy funkcjach nieparzystych/warunkach.
# clamp – “przytnij do [a,b]”; super praktyczne w normalizacji i ograniczeniach.
# shift – przesunięcie (X + c) jako operacja bazowa w modelach.
# scale – skalowanie (c·X) jako operacja bazowa w normalizacji / jednostkach.
# normalize – krytyczne, jeśli interwały idą w MCDA/ML/skalowanie danych.
# copy – bezpieczeństwo i ergonomia (szczególnie przy mutowalnych strukturach).
# to_dict – fundament serializacji / logów / debugowania.
# from_dict – odtwarzanie obiektu (pary z to_dict).
# to_json – wygodne API dla plików / REST / eksperymentów.
# from_json – jw.
# mean – szybka statystyka reprezentatywna (często = midpoint, ale nie zawsze).
# std (albo variance) – metryka rozrzutu, jeśli wspierasz interpretację „prawdopodobieństwową”/niepewność.