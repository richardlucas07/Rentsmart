# RentSmart — Sistema de Orçamento de Locação

Aplicação em Python, com Programação Orientada a Objetos, que calcula o orçamento de locação da **R.M Imóveis** e gera a projeção dos 12 primeiros meses em CSV.

Trabalho da disciplina *Algorithmic Thinking & Introduction to Object-Oriented Programming*.

## Como executar

Requisito: Python 3.8 ou superior (não precisa instalar nenhuma biblioteca).

```bash
python rentsmart.py
```

Responda às perguntas no terminal. Ao final, o programa mostra o orçamento e cria o arquivo `projecao_12_meses.csv` na mesma pasta.

## Regras de negócio

| Imóvel | Aluguel-base | Adicionais | Desconto |
|---|---|---|---|
| Apartamento | R$ 700,00 | 2 quartos: + R$ 200,00 · Garagem: + R$ 300,00 | 5% se não tiver crianças (aplicado depois dos adicionais) |
| Casa | R$ 900,00 | 2 quartos: + R$ 250,00 · Garagem: + R$ 300,00 | — |
| Estúdio | R$ 1.200,00 | Pacote de 2 vagas: + R$ 250,00 · Vaga extra: + R$ 60,00 cada | — |

Taxa contratual: R$ 2.000,00, em até 5 parcelas. É mostrada separada do aluguel.

## Estrutura de classes

- `Imovel` — classe base com o cálculo comum (base + adicionais − desconto).
- `Apartamento`, `Casa`, `Estudio` — herdam de `Imovel` e definem seus próprios adicionais e descontos.
- `Contrato` — taxa contratual e parcelamento.
- `Orcamento` — junta imóvel e contrato, exibe o resumo e gera o CSV.

## Exemplo

Apartamento, 2 quartos, com garagem, sem crianças, taxa em 5x:

```
Aluguel-base                            R$ 700,00
(+) Segundo quarto                      R$ 200,00
(+) Vaga de garagem                     R$ 300,00
(-) Desconto de 5% (sem crianças)        R$ 60,00
ALUGUEL MENSAL                        R$ 1.140,00
Taxa contratual: 5x de R$ 400,00
```

## Arquivos

- `rentsmart.py` — código-fonte
- `projecao_12_meses.csv` — gerado ao executar o programa
- `README.md` — este arquivo
