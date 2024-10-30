import unittest


def convert_array(array):
    """
    Convierte un Array de Strings y/o JSON String a un único String que enviar a otro módulo.
    :param array:
    :return:
    """
    try:
        return '--!--##-->>DELIMITER<<--##--!--'.join(array)
    except Exception as e:
        print(f'\nError in sender.convert_array(): \n{str(e)}')
        return None


def convert_string(string):
    """
    Convierte un String con formato de Array a un Array real.
    :param string:
    :return:
    """
    try:
        if string.find("--!--##-->>DELIMITER<<--##--!--") == -1:
            raise Exception
        return string.split("--!--##-->>DELIMITER<<--##--!--")
    except Exception as e:
        print(f'\nError in sender.convert_string(): \n{str(e)}')
        return None


# Clase de test
class Test(unittest.TestCase):

    # Test para verificar que la suma de dos números positivos es correcta
    def test_convert_array(self):
        input = ["Hola mundo", "{\"mensaje\":\"Hola mundo\"}"]

        output = convert_array(input)

        target = 'Hola mundo--!--##-->>DELIMITER<<--##--!--{"mensaje":"Hola mundo"}'

        self.assertEqual(output, target)

    # Test para verificar que la suma de un número positivo y uno negativo es correcta
    def test_convert_string(self):
        input = "Hola mundo--!--##-->>DELIMITER<<--##--!--{\"mensaje\":\"Hola mundo\"}"

        output = convert_string(input)

        target = ["Hola mundo", "{\"mensaje\":\"Hola mundo\"}"]

        self.assertEqual(output, target)


# Ejecuta los tests
if __name__ == '__main__':
    unittest.main()
