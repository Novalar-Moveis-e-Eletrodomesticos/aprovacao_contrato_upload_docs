from src.services.busca_contrato.busca_contrato_service import BuscaContratoService

class BuscaContratoController:
    def fetchBuscaContrato(pedido,filialid):
        data = BuscaContratoService.busca_contrato(v_pedido=pedido,v_idfilial=filialid)
        return data