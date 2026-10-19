[分割版目次](../README.md) | [前へ](06-transaction-execution.md) | [次へ](08-message-call.md) | [単一ページ版](../../ethereum_yellow_paper_ja.md)

<span id="ch:create"></span>

# 7. コントラクト作成

<div id="endow">

</div>

アカウント作成にはいくつかの固有パラメータを用いる。送信者 $`s`$ 、元のトランザクション起点者[^10] $`o`$ 、利用可能 gas $`g`$ 、実効 gas 価格 $`p`$ 、付与額 $`v`$ 、任意長バイト配列である初期化 EVM コード $`\mathbf{i}`$ 、現在のメッセージ呼び出し／コントラクト作成スタック深度 $`e`$ 、新しいアカウント・アドレスの salt $`\zeta`$ 、最後に状態変更の許可 $`w`$ である。salt $`\zeta`$ は存在しない場合がある（ $`\zeta = \varnothing`$ ）。形式的には

<span id="eq-92"></span>

```math
\zeta \in \mathbb{B}_{32} \cup \mathbb{B}_{0} \qquad \text{(92)}
```

である。[CREATE2](../appendices/appendix-h-virtual-machine.md#create2) による作成なら $`\zeta \neq \varnothing`$ となる。

作成関数 $`\Lambda`$ を形式的に定義する。この関数は、これらの値に状態 $`\boldsymbol{\sigma}`$ と累積サブ状態 $`A`$ を合わせて評価し、新しい状態、残存gas、新しい累積サブ状態、ステータス・コード、出力からなるタプル $`(\boldsymbol{\sigma}', g', A', z, \mathbf{o})`$ を返す。

<span id="eq-93"></span>

```math
(\boldsymbol{\sigma}', g', A', z, \mathbf{o}) \equiv \Lambda(\boldsymbol{\sigma}, A, s, o, g, p, v, \mathbf{i}, e, \zeta, w) \qquad \text{(93)}
```

新しいアカウントのアドレスは、送信者と[アカウントnonce](04-blocks-state-transactions.md#account_nonce)だけを含む構造を[RLP](../appendices/appendix-b-rlp.md#rlp)符号化し、そのKeccak-256ハッシュの右端160ビットを取ったものとして定義される。[CREATE2](../appendices/appendix-h-virtual-machine.md#create2)では規則が異なり、[(Buterin 2018)](../references.md#ref-EIP-1014)によるEIP-1014に記述されている。二つの場合を合わせ、新しいアカウントの結果アドレス $`a`$ を次のように定義する。

<span id="eq-94"></span><span id="eq-95"></span><span id="eq-96"></span><span id="eq:new-address"></span>

```math
\begin{aligned}
a & \equiv \mathtt{ADDR}(s, \boldsymbol{\sigma}[s]_{\mathrm{n}} - 1, \zeta, \mathbf{i}) & \qquad \text{(94)} \\
\mathtt{ADDR}(s, n, \zeta, \mathbf{i}) & \equiv \mathcal{B}_{96..255}\Big(\mathtt{KEC}\big( L_{\mathrm{A}}(s, n, \zeta, \mathbf{i})\big) \Big) & \qquad \text{(95)} \\
L_{\mathrm{A}}(s, n, \zeta, \mathbf{i}) & \equiv \begin{cases}
\mathtt{RLP}\big(\;(s, n)\;\big) & \text{if}\ \zeta = \varnothing \\
(255) \cdot s \cdot \zeta \cdot \mathtt{KEC}(\mathbf{i}) & \text{otherwise}
\end{cases} & \qquad \text{(96)}
\end{aligned}
```

ここで $`\cdot`$ はバイト配列の連結であり、 $`\mathcal{B}_{a..b}(X)`$ はバイナリ・データ $`X`$ の添字範囲 $`[a, b]`$ のビットを含むバイナリ値へ評価される。また $`\boldsymbol{\sigma}[x]`$ は $`x`$ のアドレス状態であり、存在しなければ $`\varnothing`$ である。送信者のnonce値より1小さい値を用いることに注意されたい。この呼出しに先立って送信者アカウントのnonceを増加させたと仮定しているため、用いる値は、その原因となったトランザクションまたはVM演算の開始時点における送信者のnonceである。

新しいアカウントのアドレスをアクセス済みアカウント集合へ追加する。

<span id="eq-97"></span>

```math
A^{*} \equiv A \quad \text{except} \quad A^{*}_{\mathbf{a}} \equiv A_{\mathbf{a}} \cup \{a\} \qquad \text{(97)}
```

アカウントのnonceは初期値1、残高は渡された値、ストレージは空、コード・ハッシュは空文字列のKeccak 256ビット・ハッシュとして定義される。また送信者の残高から渡された値を減じる。したがって変更後の状態は $`\boldsymbol{\sigma}^{*}`$ となる。

<span id="eq-98"></span>

```math
\boldsymbol{\sigma}^{*} \equiv \boldsymbol{\sigma} \quad \text{except:} \qquad \text{(98)}
```

<span id="eq-99"></span><span id="eq-100"></span><span id="eq-101"></span>

```math
\begin{aligned}
\boldsymbol{\sigma}^{*}[a] &=& \big( 1, v + v', \mathtt{TRIE}(\varnothing), \mathtt{KEC}\big(()\big) \big) & \qquad \text{(99)} \\
\boldsymbol{\sigma}^{*}[s] &=& \begin{cases}
\varnothing & \text{if}\ \boldsymbol{\sigma}[s] = \varnothing \ \wedge\ v = 0 \\
\mathbf{a}^{*} & \text{otherwise}
\end{cases} & \qquad \text{(100)} \\
\mathbf{a}^{*} &\equiv& (\boldsymbol{\sigma}[s]_{\mathrm{n}}, \boldsymbol{\sigma}[s]_{\mathrm{b}} - v, \boldsymbol{\sigma}[s]_{\mathbf{s}}, \boldsymbol{\sigma}[s]_{\mathrm{c}}) & \qquad \text{(101)}
\end{aligned}
```

ここで、アカウントが以前から存在していた場合、 $`v'`$ はその既存の残高である。

<span id="eq-102"></span>

```math
v' \equiv \begin{cases}
0 & \text{if} \quad \boldsymbol{\sigma}[a] = \varnothing\\
\boldsymbol{\sigma}[a]_{\mathrm{b}} & \text{otherwise}
\end{cases} \qquad \text{(102)}
```

最後に、実行モデル（[第9節](09-execution-model.md#ch:model)参照）に従って初期化 EVM コード $`\mathbf{i}`$ を実行し、アカウントを初期化する。コード実行は、実行状態の内部に限られない複数の事象を生じ得る。アカウントのストレージを変更し、別のアカウントを作成し、別のメッセージ呼び出しを行える。したがってコード実行関数 $`\Xi`$ の値は、結果状態 $`\boldsymbol{\sigma}^{**}`$ 、残りの利用可能 gas $`g^{**}`$ 、結果として得られる累積サブ状態 $`A^{**}`$ 、アカウントの本体コード $`\mathbf{o}`$ のタプルである。

<span id="eq-103"></span>

```math
(\boldsymbol{\sigma}^{**}, g^{**}, A^{**}, \mathbf{o}) \equiv \Xi(\boldsymbol{\sigma}^{*}, g, A^{*}, I) \qquad \text{(103)}
```

ここで $`I`$ は[実行環境](09-execution-model.md#exec_env)のパラメータを含む。すなわち、

<span id="eq-104"></span><span id="eq-105"></span><span id="eq-106"></span><span id="eq-107"></span><span id="eq-108"></span><span id="eq-109"></span><span id="eq-110"></span><span id="eq-111"></span><span id="eq-112"></span>

```math
\begin{aligned}
I_{\mathrm{a}} & \equiv & a & \qquad \text{(104)} \\
I_{\mathrm{o}} & \equiv & o & \qquad \text{(105)} \\
I_{\mathrm{p}} & \equiv & p & \qquad \text{(106)} \\
I_{\mathbf{d}} & \equiv & () & \qquad \text{(107)} \\
I_{\mathrm{s}} & \equiv & s & \qquad \text{(108)} \\
I_{\mathrm{v}} & \equiv & v & \qquad \text{(109)} \\
I_{\mathbf{b}} & \equiv & \mathbf{i} & \qquad \text{(110)} \\
I_{\mathrm{e}} & \equiv & e & \qquad \text{(111)} \\
I_{\mathrm{w}} & \equiv & w & \qquad \text{(112)}
\end{aligned}
```

この呼出しには入力データがないため、 $`I_{\mathbf{d}}`$ は空タプルへ評価される。 $`I_{\mathrm{H}}`$ に特別な扱いはなく、ブロックチェーンから決定される。

コード実行は gas を消費し、gas はゼロ未満になれないため、コードが自然な停止状態へ達する前に実行が終了することがある。この場合（およびほかのいくつかの例外的場合）、gas 不足（OOG）例外が発生したという。評価結果の状態は空集合 $`\varnothing`$ と定義し、作成操作全体は状態へ影響せず、実質的に作成を試みる直前の状態を残す。

初期化コードが正常に完了した場合、作成されたコントラクトのコード・サイズに比例する最終的なコントラクト作成コスト、すなわちコード格納コスト $`c`$ が支払われる。

<span id="eq-113"></span>

```math
c \equiv G_{\mathrm{codedeposit}} \times \lVert \mathbf{o} \rVert \qquad \text{(113)}
```

これを支払うだけの gas が残っていない、すなわち $`g^{**} < c`$ の場合も gas 不足例外を宣言する。

このような例外条件では残り gas はゼロとなる。すなわち、トランザクションの受信によりコントラクト作成が行われた場合でも、コントラクト作成の固有コストの支払いには影響せず、いずれにせよ支払われる。ただし gas 不足時にはトランザクションの値を作成が中断されたコントラクトのアドレスへ移転せず、コントラクトのコードも格納しない。

このような例外が発生しなければ、残り gas を起点者へ払い戻し、変更後の状態を永続化できる。したがって、結果状態、gas、累積サブ状態、ステータス・コードを形式的に $`(\boldsymbol{\sigma}', g', A', z)`$ と規定する。

<span id="eq-114"></span><span id="eq-115"></span><span id="eq-116"></span><span id="eq-117"></span><span id="eq-118"></span>

```math
\begin{aligned}
\quad g' \equiv & \begin{cases}
0 & \text{if} \quad F \\
g^{**} - c & \text{otherwise} \\
\end{cases} & \qquad \text{(114)} \\
\quad \boldsymbol{\sigma}' \equiv & \begin{cases}
\boldsymbol{\sigma} & \text{if} \quad F \ \lor\ \boldsymbol{\sigma}^{**} = \varnothing \\
\boldsymbol{\sigma}^{**} \quad \text{except:} & \\
\quad\boldsymbol{\sigma}'[a] = \varnothing & \text{if} \quad \mathtt{DEAD}(\boldsymbol{\sigma}^{**}, a) \\
\boldsymbol{\sigma}^{**} \quad \text{except:} & \\
\quad\boldsymbol{\sigma}'[a]_{\mathrm{c}} = \texttt{KEC}(\mathbf{o}) & \text{otherwise}
\end{cases} & \qquad \text{(115)} \\
\quad A' \equiv & \begin{cases}
A^{*} & \text{if} \quad F \ \lor\ \boldsymbol{\sigma}^{**} = \varnothing \\
A^{**} & \text{otherwise} \\
\end{cases} & \qquad \text{(116)} \\
\quad z \equiv & \begin{cases}
0 & \text{if} \quad F \ \lor\ \boldsymbol{\sigma}^{**} = \varnothing \\
1 & \text{otherwise}
\end{cases} & \qquad \text{(117)} \\
\text{where} \\
F \equiv  & \big( \boldsymbol{\sigma}[a] \neq \varnothing \ \wedge\ \big(\boldsymbol{\sigma}[a]_c \neq \texttt{KEC}\big(()\big) \vee \boldsymbol{\sigma}[a]_n \neq 0 \big) \big) \quad \vee & \qquad \text{(118)} \\
&(\boldsymbol{\sigma}^{**} = \varnothing \ \wedge\ \mathbf{o} = \varnothing) \quad \vee \\
&g^{**} < c \quad \vee \\
&\lVert \mathbf{o} \rVert > 24576 \quad \vee \\
&\mathbf{o}[0] = \texttt{0xef}
\end{aligned}
```

<span id="contract_creation_result"></span>

$`F`$ の最後の条件は、コントラクト・コードがバイト `0xef` で始まってはならないことを示す点に注意されたい（[(Beregszaszi et al. 2021)](../references.md#ref-EIP-3541)によるEIP-3541を参照）。

$`\boldsymbol{\sigma}'`$ の決定における但し書きは、初期化コード実行の結果バイト列 $`\mathbf{o}`$ が、新たに作成されたアカウントの最終的な本体コードを指定することを定める。

意図する結果は、付与額を伴う新しいコントラクトの作成成功か、値の移転を伴わない新規コントラクトの不作成のいずれかである。さらに、初期化コードの実行が[リバート](../appendices/appendix-h-virtual-machine.md#REVERT)した場合（ $`\boldsymbol{\sigma}^{**} = \varnothing \ \wedge\ \mathbf{o} \neq \varnothing`$ ）、ほかの例外がなければ結果 gas $`g'`$ は枯渇しないが、新しいアカウントは作成されない。

## 7.1. 微妙な点

初期化コードの実行中、新たに作成されたアドレスは存在するが、固有の本体コードを持たない[^11]。したがって、この間に受け取るメッセージ呼び出しではコードを実行しない。初期化実行が SELFDESTRUCT 命令で終わる場合、トランザクション完了前にアカウントが削除されるため問題にならない。通常の STOP コードの場合、または返されたコードが空の場合、状態にはゾンビ・アカウントが残り、残高は永久にそのアカウントへロックされる。

[^10]: トランザクションが直接引き起こしたのではなく、EVMコードの実行から生じたメッセージ呼び出しまたはコントラクト作成の場合、これは送信者と異なり得る。

[^11]: 初期化コードの実行中、そのアドレスに対する `EXTCODESIZE` はアカウントのコード長であるゼロを返し、`CODESIZE` は初期化コードの長さを返すべきである（[付録H.2](../appendices/appendix-h-virtual-machine.md#subsec:instruction-set)で定義）。
