from text import __init__

class Test___init____clean_text:
    def test__clean_text_1(self):
        result = __init__._clean_text(["Foo bar", "Hello, world!", "Hello, world!", "Foo bar", "Foo bar", "foo bar", "Hello, world!", "This is a Text"], ["Michael", "Pierre Edouard", "Anas", "Pierre Edouard", "Jean-Philippe", "George", "Michael", "Edmond"])

    def test__clean_text_2(self):
        result = __init__._clean_text(["Hello, world!", "This is a Text", "Foo bar", "This is a Text", "This is a Text", "Hello, world!", "Hello, world!", "foo bar"], ["Michael", "Michael", "Edmond", "Anas", "Jean-Philippe", "Anas", "Pierre Edouard", "Pierre Edouard"])

    def test__clean_text_3(self):
        result = __init__._clean_text(["Foo bar", "This is a Text", "This is a Text", "foo bar", "This is a Text", "Foo bar", "Foo bar", "Foo bar"], ["Pierre Edouard", "Edmond", "George", "Michael", "Edmond", "Pierre Edouard", "Edmond", "Anas"])

    def test__clean_text_4(self):
        result = __init__._clean_text(["Hello, world!", "This is a Text", "Hello, world!", "foo bar", "foo bar", "Hello, world!", "Foo bar", "Hello, world!"], ["Pierre Edouard", "Edmond", "Michael", "Michael", "Jean-Philippe", "George", "Pierre Edouard", "Anas"])

    def test__clean_text_5(self):
        result = __init__._clean_text(["Foo bar", "foo bar", "foo bar", "This is a Text", "foo bar", "Hello, world!", "Hello, world!", "Hello, world!"], ["Edmond", "Anas", "Jean-Philippe", "Michael", "Edmond", "Edmond", "Michael", "Michael"])

    def test__clean_text_6(self):
        result = __init__._clean_text([], [])

