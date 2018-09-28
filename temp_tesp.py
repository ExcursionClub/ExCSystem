class Test(object):

    def test_func(self, data):
        print("In the test func")
        print(f"got data={data}")
        print()

    def run(self):
        func = getattr(self, "test_func")
        func("test")


test = Test()
test.run()