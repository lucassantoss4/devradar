"""
worker.py — DevRadar Pipeline Worker Entry Point

Script CLI puro que instancia o Pipeline, executa o scan completo
e termina com exit code 0 (sucesso) ou 1 (falha).

Este script é projetado para ser invocado por um orquestrador externo (ex: Kestra):

    python worker.py                # roda todos os scanners
    python worker.py --premios      # roda apenas premiações
    python worker.py --eventos      # roda apenas eventos

Zero Flask, zero servidor HTTP.
"""
import sys
import logging
import argparse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("Worker")


def parse_args():
    parser = argparse.ArgumentParser(description="DevRadar Pipeline Worker")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--premios", action="store_true", help="Roda apenas o scanner de premiações")
    group.add_argument("--eventos", action="store_true", help="Roda apenas o scanner de eventos")
    return parser.parse_args()


def main():
    args = parse_args()

    logger.info("=" * 50)
    logger.info(">>> DevRadar Worker — Iniciando <<<")
    logger.info("=" * 50)

    try:
        from core.pipeline import Pipeline
        pipe = Pipeline()

        if args.premios:
            logger.info("Modo: apenas PREMIAÇÕES")
            pipe._processar_premios()
        elif args.eventos:
            logger.info("Modo: apenas EVENTOS")
            pipe._processar_eventos()
        else:
            logger.info("Modo: SCAN COMPLETO")
            pipe.run_full_scan()

        logger.info("=" * 50)
        logger.info(">>> Worker finalizado com SUCESSO (exit 0) <<<")
        logger.info("=" * 50)
        sys.exit(0)

    except Exception as e:
        logger.error("=" * 50)
        logger.error(f">>> Worker finalizado com ERRO: {e} <<<")
        logger.error("=" * 50)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
