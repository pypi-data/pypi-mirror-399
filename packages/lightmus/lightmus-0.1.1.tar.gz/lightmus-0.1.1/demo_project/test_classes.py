"""Tests for class features and OOP concepts."""


class TestBasicClass:
    def test_init(self):
        class Person:
            def __init__(self, name):
                self.name = name

        p = Person("Alice")
        assert p.name == "Alice"

    def test_method(self):
        class Counter:
            def __init__(self):
                self.count = 0

            def increment(self):
                self.count += 1

        c = Counter()
        c.increment()
        c.increment()
        assert c.count == 2

    def test_class_variable(self):
        class Dog:
            species = "Canis familiaris"

        d1 = Dog()
        d2 = Dog()
        assert d1.species == d2.species

    def test_instance_variable(self):
        class Dog:
            def __init__(self, name):
                self.name = name

        d1 = Dog("Rex")
        d2 = Dog("Buddy")
        assert d1.name != d2.name


class TestInheritance:
    def test_simple_inheritance(self):
        class Animal:
            def speak(self):
                return "sound"

        class Dog(Animal):
            def speak(self):
                return "woof"

        d = Dog()
        assert d.speak() == "woof"

    def test_super(self):
        class Parent:
            def greet(self):
                return "Hello"

        class Child(Parent):
            def greet(self):
                return super().greet() + " World"

        c = Child()
        assert c.greet() == "Hello World"

    def test_isinstance_inheritance(self):
        class Animal:
            pass

        class Dog(Animal):
            pass

        d = Dog()
        assert isinstance(d, Dog)
        assert isinstance(d, Animal)

    def test_multiple_inheritance(self):
        class A:
            def method(self):
                return "A"

        class B:
            def method(self):
                return "B"

        class C(A, B):
            pass

        c = C()
        assert c.method() == "A"


class TestMagicMethods:
    def test_str(self):
        class Point:
            def __init__(self, x, y):
                self.x = x
                self.y = y

            def __str__(self):
                return f"({self.x}, {self.y})"

        p = Point(3, 4)
        assert str(p) == "(3, 4)"

    def test_repr(self):
        class Point:
            def __init__(self, x, y):
                self.x = x
                self.y = y

            def __repr__(self):
                return f"Point({self.x}, {self.y})"

        p = Point(3, 4)
        assert repr(p) == "Point(3, 4)"

    def test_eq(self):
        class Point:
            def __init__(self, x, y):
                self.x = x
                self.y = y

            def __eq__(self, other):
                return self.x == other.x and self.y == other.y

        p1 = Point(1, 2)
        p2 = Point(1, 2)
        p3 = Point(3, 4)
        assert p1 == p2
        assert p1 != p3

    def test_len(self):
        class Stack:
            def __init__(self):
                self.items = []

            def __len__(self):
                return len(self.items)

            def push(self, item):
                self.items.append(item)

        s = Stack()
        s.push(1)
        s.push(2)
        assert len(s) == 2

    def test_getitem(self):
        class MyList:
            def __init__(self, items):
                self.items = items

            def __getitem__(self, index):
                return self.items[index]

        ml = MyList([10, 20, 30])
        assert ml[1] == 20

    def test_contains(self):
        class Bag:
            def __init__(self, items):
                self.items = set(items)

            def __contains__(self, item):
                return item in self.items

        b = Bag([1, 2, 3])
        assert 2 in b
        assert 5 not in b


class TestProperties:
    def test_property_getter(self):
        class Circle:
            def __init__(self, radius):
                self._radius = radius

            @property
            def radius(self):
                return self._radius

        c = Circle(5)
        assert c.radius == 5

    def test_property_setter(self):
        class Circle:
            def __init__(self, radius):
                self._radius = radius

            @property
            def radius(self):
                return self._radius

            @radius.setter
            def radius(self, value):
                if value < 0:
                    raise ValueError("Radius cannot be negative")
                self._radius = value

        c = Circle(5)
        c.radius = 10
        assert c.radius == 10

    def test_computed_property(self):
        class Rectangle:
            def __init__(self, width, height):
                self.width = width
                self.height = height

            @property
            def area(self):
                return self.width * self.height

        r = Rectangle(3, 4)
        assert r.area == 12


class TestClassMethod:
    def test_classmethod(self):
        class Counter:
            count = 0

            @classmethod
            def increment(cls):
                cls.count += 1

        Counter.increment()
        Counter.increment()
        assert Counter.count == 2

    def test_staticmethod(self):
        class Math:
            @staticmethod
            def add(a, b):
                return a + b

        assert Math.add(2, 3) == 5
