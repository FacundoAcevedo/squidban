class Registro:
    """Representa una entrada de un archivo"""
    pass

    def __str__(self):
        """Para poder printear los artibutos en caso de debug"""
        return str(self.__dict__)

    def getAsDict(self):
        """Devuelvo un diccionario con los atributos"""
        return self.__dict__