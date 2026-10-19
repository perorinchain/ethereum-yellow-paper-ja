[分割版目次](../README.md) | [前へ](02-blockchain-paradigm.md) | [次へ](04-blocks-state-transactions.md) | [単一ページ版](../../ethereum_yellow_paper_ja.md)

<span id="ch:conventions"></span>

# 3. 表記規約

形式的記法にはいくつかの組版上の規約を用いる。その一部は本稿にかなり固有のものである。

高度に構造化された「最上位」の状態値の二つの集合は、太字のギリシャ小文字で表す。これらは、 $`\boldsymbol{\sigma}`$ （またはその変種）で表すワールド状態と、 $`\boldsymbol{\mu}`$ で表すマシン状態に分類される。

高度に構造化された値を操作する関数は、Ethereum 状態遷移関数 $`\Upsilon`$[↗](02-blockchain-paradigm.md#Upsilon_state_transition) のように、ギリシャ大文字で表す。

大部分の関数には大文字のラテン文字を用いる。たとえば $`C`$ は一般コスト関数である。特殊化した変種を表すため添字を付けることがあり、たとえば $`C_\text{SSTORE}`$[↗](../appendices/appendix-h-virtual-machine.md#C__SSTORE) は [SSTORE](../appendices/appendix-h-virtual-machine.md#SSTORE) 演算のコスト関数である。特殊化された関数や外部で定義される可能性のある関数は、タイプライタ体で表すことがある。たとえば Keccak-256 ハッシュ関数（最終版 SHA-3 仕様ではなく、[(Bertoni et al. 2011)](../references.md#ref-Keccak) による SHA-3 コンテスト優勝案の第3版に基づく）は $`\texttt{KEC}`$ と表し、通常は単に Keccak と呼ぶ。また $`\texttt{KEC512}`$ は Keccak-512 ハッシュ関数を指す。

タプルは通常、大文字で表す。たとえば $`T`$ は Ethereum のトランザクションを表す。この記号は、そのように定義されていれば、個々の構成要素を参照する添字を付けられる。たとえば $`T_{\mathrm{n}}`$[↗](06-transaction-execution.md#transaction_nonce) は当該トランザクションの nonce を表す。添字の字体はその型を示すために用いる。たとえば大文字の添字は、添字で構成要素を参照できるタプルを示す。

スカラーと固定長バイト列（同義語として配列）は、通常の小文字で表す。たとえば本書では $`n`$ を[トランザクション nonce](06-transaction-execution.md#transaction_nonce) の表記に用いる。特に固有の意味を持つものにはギリシャ文字を用いることがあり、たとえば $`\delta`$ は所与の演算がスタック上に必要とする項目数である。

任意長の列は通常、太字の小文字で表す。たとえば $`\mathbf{o}`$ はメッセージ呼び出しの出力データとして与えられるバイト列を表す。特に重要な値には太字の大文字を用いることがある。

本書を通じて、スカラーは非負整数であり、したがって集合 $`\mathbb{N}`$ に属すると仮定する。すべてのバイト列からなる集合を $`\mathbb{B}`$ とし、[付録B](../appendices/appendix-b-rlp.md#app:rlp)で形式的に定義する。列の集合を特定の長さのものに制限する場合は添字で表す。したがって、長さ32のすべてのバイト列からなる集合を $`\mathbb{B}_{32}`$ 、 $`2^{256}`$ 未満のすべての非負整数からなる集合を $`\mathbb{N}_{256}`$ と呼ぶ。これは[第4.4節](04-blocks-state-transactions.md#subsec:The_Block)で形式的に定義する。

角括弧は、列の個々の構成要素または部分列に索引付けして参照するために用いる。たとえば $`\boldsymbol{\mu}_{\mathbf{s}}[0]`$ はマシンのスタック上の最初の項目を表す。部分列では、省略記号を使って両端の要素を含む範囲を指定する。たとえば $`\boldsymbol{\mu}_{\mathbf{m}}[0..31]`$ はマシン・メモリの最初の32項目を表す。

それ自体がタプルであるアカウントの列からなる大域状態 $`\boldsymbol{\sigma}`$ の場合、角括弧は個々のアカウントを参照するために用いる。

既存値の変種を考えるときは、所与の定義スコープ内で、変更前の「入力」値をプレースホルダ $`\Box`$ で表すと仮定すれば、変更後の利用可能な値を $`\Box'`$ 、中間値を $`\Box^{*}`$ 、 $`\Box^{**}`$ などと表す、という規則に従う。ごく特殊な場合には、可読性を最大にするため、かつ意味に曖昧さがない場合に限って、特に注目すべき中間値を英数字の添字で表すことがある。

既存関数の利用を考えるとき、関数 $`f`$ に対する関数 $`f^{*}`$[↗](04-blocks-state-transactions.md#general_element_wise_sequence_transformation_f_pow_asterisk) は、列同士を写像する、同様の要素単位版の関数を表す。これは[第4.4節](04-blocks-state-transactions.md#subsec:The_Block)で形式的に定義する。

本書を通じて、有用な関数をいくつか定義する。よく用いるものの一つが $`\ell`$ であり、所与の列の最後の項目を値とする。

<span id="eq-6"></span>

```math
\ell(\mathbf{x}) \equiv \mathbf{x}[\lVert \mathbf{x} \rVert - 1] \qquad \text{(6)}
```
