
# Arquitecturas web · conceptos previos

* Concurrencia
    * Propiedad de un sistema, que representa el hecho de que múltiples actividades
    se ejecutan simultáneamente.
    * Programación concurrente: 
      Es la composición de módulos que se ejecutan independientemente, de forma
      asíncrona y no determinista.
    * Hace referencia a propiedad conceptual de un programa, ya sea  single-core, multi-core o distribuido.

* Paralelismo
    * Es una propiedad de *tiempo de ejecución* (no conceptual)
    * Hace falta más de un procesador, o bién sistema distribuido
    * Es una forma de ejecutar programas concurrentes 

---

# Arquitecturas web · conceptos previos
    
* Escalabilidad
    * Propiedad de un sistema, que describe la habilidad de gestionar subidas
    y bajadas de carga de trabajo apropiadamente
    * Vertical: Más recursos a un sólo nodo: CPU, Memoria, Disco...
    * Horizontal: Más nodos en el sistema

* Escalabilidad y concurrencia
    * Íntimamente relacionados
    * La concurrencia puede hacer a una aplicación escalable
    * Mediante concurrencia y paralelismo, podemos exprimir las caracteríasticas 
      del hardware (Ej: extender ejecución a múltiples cores)

# Presenter Notes

 Introducimos modelos de concurrencia, para exponer problemática y acabar viendo
 porqué usamos procesos simples, sincronos, bloqueantes.


---

# Aplicación web 

<img src='img/LSBAWS_HTTP_request_response.png' />

---

# Rendimiento web

En términos de peticiones y respuestas web, métricas interesantes:

* Throughput (#peticiones/seg)
* Tiempo de respuesta (ms)
* Transferencia (Mbps) 
* Número de peticiones concurrentes

Y las  estadísticas a mirar en el servidor: 

* Uso de CPU
* Carga 
* **Memoria usada**
* Número de procesos, threads, sockets, descriptores de fichero...

---

# Arquitectura web escalable: El objetivo

* Resumiendo el problema:
    * Queremos gestionar tantas peticiones en paralelo como sea posible
    * Tan rápido como sea posible
    * **Con los mínimos recursos necesarios!!**
    
Otra forma de verlo: el uso de recursos aumenta y escala con la carga.

* Dos extremos de ejemplo: 
    * Somos pobres y queremos que funcione con la mínima instancia de heroku.
    * Queremos escalar miles de peticiones en Amazon, y pero pagar el mínimo necesario.
    * En el centro, tenemos un servidor dedicado sobrado: no es crucial para nosotros consumir el mínimo posible.

---

# Arquitectura web escalable: El problema

* Queremos servir concurrentemente las peticiones. Necesitamos mapear conexiones y
  y peticiones a algún modelo de programación concurrente. 
* Queremos **escalar** horizontalmente
* **Queremos usar el mínimo de recursos**
* Sabemos que las peticiones concurrentes provocarán una **mezcla de I/O y CPU**
    * En apps donde se deben hacer peticiones síncronas para el cliente, 
    como una dispo hotelera, el porcentaje de I/O se puede disparar.


---

# Formas de gestionar I/O

Modos de I/O a bajo nivel en Linux:

<img src='img/io.png' />

* Para arquitectura web, nos interesa diferenciar entre síncrono/bloqueante, y el resto. 
* Nos referimos a los otros tres modelos como como *event driven*
    * Ejemplos componentes asíncronos orientados a eventos
        * Web servers: nginx
        * Librerías python: twisted, asyncio, aiohttp, gevent, tornado, crossbar.io
        * frameworks python:  API-Hour, klein 

---

# Arquitecturas web Prefork

<img src='img/process-arch.svg' />

El proceso principal abre socket, crea procesos hijos y comparte socket con ellos. 
Cada *request handler*  bloquea esperando conexion.

---

# Diseño de arquitecturas escalables: componentes

<img src='img/web_arch.svg' />

---

# Componentes de nuestra Aplicación Python

* Un servidor web con arquitectura *event-driven*, gestiona conexiones con los
  clientes web. Alto rendimiento en I/O de red y ficheros estáticos.
    * **nginx**, cherokee, lighttpd
* Servidor de aplicaciones python *en modo prefork* 
    * Gestionamos **I/O de nuestra aplicación** mediante peticiones concurrentes
    * Programación síncrona, bloqueante, deterministica.
        * Alternativa: programación concurrente en nuestra app: gevent, asyncio, tiwsted...
    
---

# Servidor aplicaciones Python


* Num workers?
    *  (2 x $num_cores) + 1
    * Dependerá de nuestro porcentaje de I/O !

* Decisiones: 
    * Procesos o threads?
    * Si gestionamos alto porcentaje I/O mediante procesos bloqueantes,
      tendremos que escalar en num procesos. La memoria será un factor importante.
    * Podemos usar *threads* para obtener más hilos concurrentes con la misma memoria.
        * Django en general es *thread safe*
            * Cuidado con los *custom template tags*
            * Problemas históricos con class based views, parece que arreglados.

---

# Referentes diseño arquitecturas aplicaciones:

* http://12factor.net
* *shared nothing*
* *Inmutable Infrastructure*

