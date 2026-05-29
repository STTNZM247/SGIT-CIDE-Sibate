va ahora vamos a mejorar el panel de http://127.0.0.1:8000/usuario/pedidos/, vamos a simplificar css codigos y mejorar funcionamientos,


comos abemos tenemos las opciones de pendiente
en espera
devuelto
cancelado
rechazado(que deberia ser soloc ancelado pues rechazaco yc ancelado es lo mismo)
entregaado

tenemos el codigo de entrega y el codigo dinamico para cuando se vence el pedido y necesita entregarlo y estan als opciones d epedir ams tiempo solo 3 solicuitudes de pedir mas tiempo



asi q vamos a mejorar todo eso, empezando con modular funciones js y css 


asi q vamosa  mirar static, vemos q hay uancc arpeta llamda css pero debajo de todas esas hay otra q dice pedidos y dentro css, que pasa hayc arpetas volando de css asi q la primera carpeta de css es donde tendremso modulados todos los css del sistema por carpetas dependiendo de q tratan, si trata el css de usario de cualquier coas de usaurios sera la carpeta usuario y adnetro encontraremos los css de ellos sean en un solo archvio o varios para mejorar carga, entonces primero modula y arregla esas carpetas, luego vamos a modular el js y css


despues de hcaer eso si editaremos el panel de http://127.0.0.1:8000/usuario/pedidos/

para mejorar eos botones de filtro q tiene arriba  y mejroar lsoc ajones de los estados del pedido 