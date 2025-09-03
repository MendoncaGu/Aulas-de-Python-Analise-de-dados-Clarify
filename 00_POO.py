class Carro:
    def __init__(self, modelo, cor):
        self.modelo = modelo 
        self.cor = cor
        self.velocidade = 0 # o carro começa parado

    def acelerar(self, incremento):
        self.velocidade += incremento
        print(f'O {self.modelo} acelerou para {self.velocidade} Km/h')

    def desacelerar(self, decremento):
        self.velocidade -= decremento
        print(f'O {self.modelo} reduziu para {self.velocidade} Km/h')

meu_carro = Carro('Fusca', 'Azul')
meu_outro_carro = Carro('BYD', 'Cinza') 

meu_carro.acelerar(20)
meu_carro.acelerar(20)
meu_carro.acelerar(20)
meu_carro.desacelerar(25)