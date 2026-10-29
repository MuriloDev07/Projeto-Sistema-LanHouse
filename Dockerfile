FROM python:3.12-slim
WORKDIR /app

# 1 - Copia apenas as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2 - Copia o resto do código do projeto
COPY . .

# 3 - Expõe a porta e arranca a aplicação
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]