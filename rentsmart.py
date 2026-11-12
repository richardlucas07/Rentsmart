"""
RentSmart - Sistema de Orçamento de Locação da R.M Imóveis.

O programa pergunta os dados da locação, calcula o aluguel mensal,
mostra o orçamento detalhado e gera um arquivo CSV com a projeção
dos 12 primeiros meses de contrato.

Como executar:  python rentsmart.py
"""

import csv


# ---------------------------------------------------------------------------
# Classes de imóveis
# ---------------------------------------------------------------------------

class Imovel:
    """Classe base: tudo o que qualquer imóvel da imobiliária tem em comum."""

    nome = "Imóvel"
    aluguel_base = 0.0

    def calcular_adicionais(self):
        """Devolve uma lista de (descrição, valor). Cada tipo de imóvel define a sua."""
        return []

    def calcular_desconto(self, subtotal):
        """Devolve (descrição, valor) do desconto. Por padrão não há desconto."""
        return ("Sem desconto", 0.0)

    def calcular_subtotal(self):
        """Aluguel-base somado a todos os adicionais."""
        total_adicionais = sum(valor for _, valor in self.calcular_adicionais())
        return self.aluguel_base + total_adicionais

    def calcular_aluguel_mensal(self):
        """Valor final do aluguel: subtotal menos o desconto."""
        subtotal = self.calcular_subtotal()
        _, desconto = self.calcular_desconto(subtotal)
        return round(subtotal - desconto, 2)


class Apartamento(Imovel):
    nome = "Apartamento"
    aluguel_base = 700.00
    ADICIONAL_DOIS_QUARTOS = 200.00
    ADICIONAL_GARAGEM = 300.00
    DESCONTO_SEM_CRIANCAS = 0.05  # 5%

    def __init__(self, quartos, tem_garagem, tem_criancas):
        self.quartos = quartos
        self.tem_garagem = tem_garagem
        self.tem_criancas = tem_criancas

    def calcular_adicionais(self):
        adicionais = []
        if self.quartos == 2:
            adicionais.append(("Segundo quarto", self.ADICIONAL_DOIS_QUARTOS))
        if self.tem_garagem:
            adicionais.append(("Vaga de garagem", self.ADICIONAL_GARAGEM))
        return adicionais

    def calcular_desconto(self, subtotal):
        # O desconto é aplicado depois dos adicionais, como pede a regra.
        if not self.tem_criancas:
            return ("Desconto de 5% (sem crianças)", round(subtotal * self.DESCONTO_SEM_CRIANCAS, 2))
        return ("Sem desconto", 0.0)


class Casa(Imovel):
    nome = "Casa"
    aluguel_base = 900.00
    ADICIONAL_DOIS_QUARTOS = 250.00
    ADICIONAL_GARAGEM = 300.00

    def __init__(self, quartos, tem_garagem):
        self.quartos = quartos
        self.tem_garagem = tem_garagem

    def calcular_adicionais(self):
        adicionais = []
        if self.quartos == 2:
            adicionais.append(("Segundo quarto", self.ADICIONAL_DOIS_QUARTOS))
        if self.tem_garagem:
            adicionais.append(("Vaga de garagem", self.ADICIONAL_GARAGEM))
        return adicionais


class Estudio(Imovel):
    nome = "Estúdio"
    aluguel_base = 1200.00
    PACOTE_DUAS_VAGAS = 250.00
    VALOR_VAGA_EXTRA = 60.00

    def __init__(self, quer_estacionamento, vagas_extras=0):
        self.quer_estacionamento = quer_estacionamento
        self.vagas_extras = vagas_extras if quer_estacionamento else 0

    def calcular_adicionais(self):
        adicionais = []
        if self.quer_estacionamento:
            adicionais.append(("Pacote de 2 vagas", self.PACOTE_DUAS_VAGAS))
            if self.vagas_extras > 0:
                descricao = f"{self.vagas_extras} vaga(s) adicional(is)"
                adicionais.append((descricao, self.vagas_extras * self.VALOR_VAGA_EXTRA))
        return adicionais


# ---------------------------------------------------------------------------
# Contrato e orçamento
# ---------------------------------------------------------------------------

class Contrato:
    """Taxa contratual: é um custo separado do aluguel, pago em 1 a 5 parcelas."""

    TAXA = 2000.00
    MAX_PARCELAS = 5

    def __init__(self, parcelas):
        self.parcelas = parcelas

    def valores_das_parcelas(self):
        """Lista com o valor de cada parcela (a última ajusta os centavos)."""
        valor = round(self.TAXA / self.parcelas, 2)
        valores = [valor] * self.parcelas
        valores[-1] = round(self.TAXA - valor * (self.parcelas - 1), 2)
        return valores


class Orcamento:
    """Junta o imóvel e o contrato, mostra o resumo e gera a projeção."""

    MESES = 12

    def __init__(self, imovel, contrato):
        self.imovel = imovel
        self.contrato = contrato

    def projecao(self):
        """Uma linha por mês: aluguel, parcela da taxa contratual e total."""
        aluguel = self.imovel.calcular_aluguel_mensal()
        parcelas = self.contrato.valores_das_parcelas()
        linhas = []
        for mes in range(1, self.MESES + 1):
            parcela = parcelas[mes - 1] if mes <= len(parcelas) else 0.0
            linhas.append({
                "mes": mes,
                "aluguel": aluguel,
                "parcela_contrato": parcela,
                "total_mes": round(aluguel + parcela, 2),
            })
        return linhas

    def exibir_resumo(self):
        imovel = self.imovel
        subtotal = imovel.calcular_subtotal()
        descricao_desconto, desconto = imovel.calcular_desconto(subtotal)
        parcelas = self.contrato.valores_das_parcelas()

        print("\n" + "=" * 50)
        print("ORÇAMENTO DE LOCAÇÃO - R.M IMÓVEIS")
        print("=" * 50)
        print(f"Imóvel: {imovel.nome}")
        print("\n--- ALUGUEL MENSAL ---")
        print(f"{'Aluguel-base':<35}{formatar(imovel.aluguel_base):>15}")
        for descricao, valor in imovel.calcular_adicionais():
            print(f"{'(+) ' + descricao:<35}{formatar(valor):>15}")
        if desconto > 0:
            print(f"{'(-) ' + descricao_desconto:<35}{formatar(desconto):>15}")
        print(f"{'ALUGUEL MENSAL':<35}{formatar(imovel.calcular_aluguel_mensal()):>15}")

        print("\n--- TAXA CONTRATUAL (custo separado) ---")
        print(f"{'Valor total da taxa':<35}{formatar(Contrato.TAXA):>15}")
        print(f"{'Parcelamento':<35}{f'{len(parcelas)}x de ' + formatar(parcelas[0]):>15}")

        print("\n--- PROJEÇÃO DOS 12 MESES ---")
        print(f"{'Mês':<6}{'Aluguel':>14}{'Taxa contrato':>16}{'Total':>14}")
        for linha in self.projecao():
            print(f"{linha['mes']:<6}{formatar(linha['aluguel']):>14}"
                  f"{formatar(linha['parcela_contrato']):>16}{formatar(linha['total_mes']):>14}")
        total_ano = sum(linha["total_mes"] for linha in self.projecao())
        print(f"{'Total no primeiro ano':<36}{formatar(total_ano):>14}")
        print("=" * 50)

    def gerar_csv(self, nome_arquivo="projecao_12_meses.csv"):
        """Grava a projeção em CSV (separador ';' para abrir direto no Excel)."""
        with open(nome_arquivo, "w", newline="", encoding="utf-8-sig") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";")
            escritor.writerow(["Mes", "Aluguel", "Parcela taxa contratual", "Total do mes"])
            for linha in self.projecao():
                escritor.writerow([
                    linha["mes"],
                    numero_csv(linha["aluguel"]),
                    numero_csv(linha["parcela_contrato"]),
                    numero_csv(linha["total_mes"]),
                ])
        return nome_arquivo


# ---------------------------------------------------------------------------
# Funções de apoio: formatação e leitura validada
# ---------------------------------------------------------------------------

def formatar(valor):
    """1234.5 -> 'R$ 1.234,50'"""
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def numero_csv(valor):
    """1234.5 -> '1234,50'"""
    return f"{valor:.2f}".replace(".", ",")


def ler_inteiro(pergunta, minimo, maximo):
    """Repete a pergunta até o usuário digitar um número inteiro dentro do intervalo."""
    while True:
        resposta = input(pergunta).strip()
        if resposta.isdigit() and minimo <= int(resposta) <= maximo:
            return int(resposta)
        print(f"  Entrada inválida. Digite um número de {minimo} a {maximo}.")


def ler_sim_nao(pergunta):
    """Repete a pergunta até o usuário responder s ou n."""
    while True:
        resposta = input(pergunta + " (s/n): ").strip().lower()
        if resposta in ("s", "sim"):
            return True
        if resposta in ("n", "nao", "não"):
            return False
        print("  Entrada inválida. Responda com s ou n.")


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------

def criar_imovel():
    """Pergunta o tipo e as características e devolve o objeto do imóvel."""
    print("\nTipos de imóvel:")
    print("  1 - Apartamento")
    print("  2 - Casa")
    print("  3 - Estúdio")
    tipo = ler_inteiro("Escolha o tipo (1 a 3): ", 1, 3)

    if tipo == 1:
        quartos = ler_inteiro("Quantos quartos (1 ou 2)? ", 1, 2)
        garagem = ler_sim_nao("Deseja vaga de garagem?")
        criancas = ler_sim_nao("Possui crianças?")
        return Apartamento(quartos, garagem, criancas)

    if tipo == 2:
        quartos = ler_inteiro("Quantos quartos (1 ou 2)? ", 1, 2)
        garagem = ler_sim_nao("Deseja vaga de garagem?")
        return Casa(quartos, garagem)

    estacionamento = ler_sim_nao("Deseja estacionamento (pacote de 2 vagas)?")
    extras = 0
    if estacionamento:
        extras = ler_inteiro("Quantas vagas adicionais além das 2 (0 a 20)? ", 0, 20)
    return Estudio(estacionamento, extras)


def main():
    print("=" * 50)
    print("RentSmart - Orçamento de Locação | R.M Imóveis")
    print("=" * 50)

    while True:
        imovel = criar_imovel()
        parcelas = ler_inteiro(
            f"Em quantas parcelas deseja pagar a taxa contratual (1 a {Contrato.MAX_PARCELAS})? ",
            1, Contrato.MAX_PARCELAS)

        orcamento = Orcamento(imovel, Contrato(parcelas))
        orcamento.exibir_resumo()
        arquivo = orcamento.gerar_csv()
        print(f"Arquivo '{arquivo}' gerado com a projeção dos 12 meses.")

        if not ler_sim_nao("\nDeseja fazer outro orçamento?"):
            print("Obrigado por usar o RentSmart!")
            break


if __name__ == "__main__":
    main()
