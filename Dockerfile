FROM python:3.12-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN adduser --disabled-password --gecos "" appuser

# 1 - Copia apenas as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2 - Copia o resto do código do projeto
COPY --chown=appuser:appuser . .

USER appuser

# 3 - Expõe a porta e roda a aplicação
EXPOSE 5000
CMD ["python", "run.py"]