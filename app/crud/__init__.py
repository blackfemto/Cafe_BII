from .categorias import (
    criar_categoria,
    listar_categorias,
    buscar_categoria,
    atualizar_categoria,
    deletar_categoria
)

from .produtos import (
    criar_produto,
    listar_produtos,
    buscar_produto,
    atualizar_produto,
    deletar_produto
)

from .comandas import (
    criar_comanda,
    listar_comandas_abertas,  # ← MUDOU DE listar_comandas PARA listar_comandas_abertas
    buscar_comanda,
    calcular_total,
    fechar_comanda,
    limpar_comandas_fechadas
)

from .itens_comanda import (
    adicionar_produto,
    diminuir_quantidade,
    remover_item
)

from .caixa import (
    get_resumo_caixa,
    get_vendas_periodo
)

from .usuario import (
    criar_usuario,
    autenticar_usuario,
    alterar_senha,
    listar_usuarios,
    desativar_usuario,
    ativar_usuario
)

from .auditoria import (
    registrar_auditoria,
    listar_auditoria
)

from .relatorios import (
    get_vendas_ultimos_7_dias,
    get_produtos_mais_vendidos,
    get_faturamento_por_categoria,
    get_resumo_geral
)

from .fechamento import (
    criar_fechamento,
    listar_fechamentos,
    get_ultimo_fechamento
)

from .historico import (
    salvar_comandas_fechadas,
    listar_historico_por_fechamento
)
