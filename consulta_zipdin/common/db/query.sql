SELECT
	pf.idfilial,
	pf.idpedidovenda,
	pv."nome",
	p.cnpj_cpf,
	pf.contratozd
FROM novalar.propostasfidc pf
LEFT JOIN rst.pedidovenda pv ON pf.idfilial = pv.idfilial AND pf.idpedidovenda = pv.idpedidovenda
JOIN glb.pessoa p ON pv.idcnpj_cpf = p.idcnpj_cpf
WHERE
     pf.idfilial = :idfilial
     AND pf.idpedidovenda = :pedido