[分割版目次](../README.md) | [前へ](05-gas-and-payment.md) | [次へ](07-contract-creation.md) | [単一ページ版](../../ethereum_yellow_paper_ja.md)

<span id="ch:transactions"></span>

# 6. トランザクションの実行

トランザクションの実行は Ethereum プロトコルで最も複雑な部分であり、状態遷移関数 $`\Upsilon`$[↗](02-blockchain-paradigm.md#Upsilon_state_transition) を定義する。実行されるトランザクションは、まず次の内在的妥当性検査に合格すると仮定する。

1.  トランザクションが整形式の RLP であり、末尾に余分なバイトがない。

2.  トランザクション署名が妥当である。

3.  [トランザクション nonce](#transaction_nonce) が妥当である（[送信者アカウントの現在の nonce](04-blocks-state-transactions.md#account_nonce) と等しい）。

4.  送信者アカウントにコントラクト・コードがデプロイされていない（[(Feist, Khovratovich, and Wijden 2021)](../references.md#ref-EIP-3607) の EIP-3607 参照）。

5.  gas 上限が、トランザクションの使用する固有gas $`g_0`$ 以上である。

6.  送信者のアカウント残高が、前払いに必要なコスト $`v_0`$ 以上である。

7.  型2では **maxFeePerGas** $`T_m`$ 、型0および型1では **gasPrice** $`T_p`$ が、ブロックの基本手数料 $`H_{\mathrm{f}}`$ 以上である。

8.  型2では **maxPriorityFeePerGas** $`T_f`$ が **maxFeePerGas** $`T_m`$ 以下である。

形式的には、 $`T`$ をトランザクション、 $`\boldsymbol{\sigma}`$ を状態として、関数 $`\Upsilon`$[↗](02-blockchain-paradigm.md#Upsilon_state_transition) を考える。

<span id="eq-61"></span>

```math
\boldsymbol{\sigma}' = \Upsilon(\boldsymbol{\sigma}, T) \qquad \text{(61)}
```

したがって $`\boldsymbol{\sigma}'`$ はトランザクション後の状態である。また、$`\Upsilon^{\mathrm{g}}`$[↗](#tx_total_gas_used_Upsilon_pow_g) を実行で使用した gas 量、$`\Upsilon^{\mathbf{l}}`$[↗](#tx_logs_Upsilon_pow_l) を累積ログ項目、$`\Upsilon^{\mathrm{z}}`$[↗](#tx_status_Upsilon_pow_z) を結果のステータス・コードと定義する。これらは後で形式的に定義する。

<span id="ch:substate"></span>

## 6.1. サブ状態

トランザクションの実行中には、トランザクション直後に処理される一定の情報を蓄積する。これを*累積トランザクション・サブ状態*、略して*累積サブ状態*と呼び、タプル $`A`$ として表す。

<span id="eq-62"></span>

```math
A \equiv (A_{\mathbf{s}}, A_{\mathbf{l}}, A_{\mathbf{t}}, A_{\mathrm{r}}, A_{\mathbf{a}}, A_{\mathbf{K}}) \qquad \text{(62)}
```

<div id="self_destruct_set_wordy_defn_A__s">

</div>

このタプルには、自己破棄集合 $`A_{\mathbf{s}}`$ 、すなわちトランザクション完了後に破棄されるアカウントの集合が含まれる。<span id="tx_log_series_wordy_defn_A__l"></span> $`A_{\mathbf{l}}`$ はログ列である。これはVMコード実行中に保存され索引付け可能な「チェックポイント」の列であり、分散型アプリケーションのフロントエンドなどEthereum世界の外部にいる観察者がコントラクト呼び出しを容易に追跡できるようにする。<span id="tx_touched_accounts_wordy_defn_A__t"></span> $`A_{\mathbf{t}}`$ は接触済みアカウントの集合であり、そのうち空のものはトランザクション終了時に削除される。<span id="refund_balance_defn_words_A__r"></span> $`A_{\mathrm{r}}`$ は還付残高であり、[SSTORE](../appendices/appendix-h-virtual-machine.md#SSTORE)命令を使用してコントラクト・ストレージを非ゼロ値からゼロへ戻すと増加する。直ちに還付されるわけではないが、総実行コストの一部を相殺できる。最後に、[(Buterin and Swende 2020a)](../references.md#ref-EIP-2929)によるEIP-2929は、<span id="accessed_addresses_defn_words_A__a"></span>アクセス済みアカウント・アドレス集合 $`A_{\mathbf{a}}`$ と、<span id="accessed_storage_keys_defn_words_A__k"></span>アクセス済みストレージ・キー集合 $`A_{\mathbf{K}}`$ を導入した（より正確には、 $`A_{\mathbf{K}}`$ の各要素は20バイトのアカウント・アドレスと32バイトのストレージ・スロットからなるタプルである）。

空の累積サブ状態 $`A^0`$ は、自己破棄、ログ、接触済みアカウント、アクセス済みストレージを持たず、還付残高がゼロで、アクセス済みアドレスにすべてのプリコンパイル済みコントラクトを含むものとして定義する。

<span id="eq-63"></span>

```math
A^0 \equiv (\varnothing, (), \varnothing, 0, \pi, \varnothing) \qquad \text{(63)}
```

ここで $`\pi`$ はすべてのプリコンパイル済みアドレスの集合である。

## 6.2. 実行

<div id="intrinsic_gas_g_0">

</div>

固有gas $`g_0`$ 、すなわちこのトランザクションが実行前に支払う必要のあるgas量を次のように定義する。

<span id="eq-64"></span>

```math
\begin{aligned}
g_0 \equiv {} & \sum_{i \in T_{\mathbf{i}}, T_{\mathbf{d}}} \begin{cases} G_{\mathrm{txdatazero}} & \text{if} \quad i = 0 \\ G_{\mathrm{txdatanonzero}} & \text{otherwise} \end{cases} & \qquad \text{(64)} \\
{} & + \begin{cases} G_{\mathrm{txcreate}} + R({\lVert T_{\mathbf{i}} \rVert}) & \text{if} \quad T_{\mathrm{t}} = \varnothing \\ 0 & \text{otherwise} \end{cases} \\
{} & + G_{\mathrm{transaction}} \\
{} & + \sum_{j = 0}^{\lVert T_{\mathbf{A}} \rVert - 1} \big( G_{\mathrm{accesslistaddress}} + \lVert T_{\mathbf{A}}[j]_{\mathbf{s}} \rVert G_{\mathrm{accessliststorage}} \big)
\end{aligned}
```

ここで $`T_{\mathbf{i}},T_{\mathbf{d}}`$ は、トランザクションがコントラクト作成かメッセージ呼び出しかに応じて、その関連データまたは初期化EVMコードのバイト列を意味する。トランザクションがコントラクトを作成する場合は $`G_{\mathrm{txcreate}}`$ を加えるが、メッセージ呼び出しの場合は加えない。 $`G_{\mathrm{accesslistaddress}}`$ と $`G_{\mathrm{accessliststorage}}`$ は、それぞれアカウントおよびストレージへのアクセスをウォーム化するコストである。 $`G`$ は[付録G](../appendices/appendix-g-fee-schedule.md#app:fees)で完全に定義する。

<div id="initcode_cost">

</div>

*initcode コスト関数* $`R`$ を、新しいコントラクトの作成コードを実行する前に initcode の各ワードについて支払う必要がある gas 量として定義する。

<span id="eq-65"></span>

```math
R(x) \equiv G_{\mathrm{initcodeword}} \times \lceil \frac{x}{32} \rceil \qquad \text{(65)}
```

<div id="effective_gas_price_p">

</div>

*実効 gas 価格* $`p`$ を、トランザクション実行中に消費した gas 1単位当たりに署名者が支払う Wei の量として定義する。次のように計算する。

<span id="eq-66"></span>

```math
p \equiv \begin{cases}
  T_{\mathrm{p}} & \text{if} \; T_{\mathrm{x}} = 0 \lor T_{\mathrm{x}} = 1 \\
  f + H_{\mathrm{f}} & \text{if} \; T_{\mathrm{x}} = 2 \\
  \end{cases} \qquad \text{(66)}
```

<div id="priority_fee_f">

</div>

ここで $`f`$ は*優先手数料*、すなわち実行中に消費した gas 1単位当たりにブロックの受益者アドレスが受け取る Wei の量である。次のように計算する。

<span id="eq-67"></span>

```math
f \equiv \begin{cases}
  T_{\mathrm{p}} - H_{\mathrm{f}} & \text{if} \; T_{\mathrm{x}} = 0 \lor T_{\mathrm{x}} = 1 \\
  min(T_{\mathrm{f}}, T_{\mathrm{m}} - H_{\mathrm{f}}) & \text{if} \; T_{\mathrm{x}} = 2 \\
  \end{cases} \qquad \text{(67)}
```

前払いコスト $`v_0`$ は次のように計算される。

<span id="eq-68"></span>

```math
v_0 \equiv \begin{cases}
  T_{\mathrm{g}}T_{\mathrm{p}} + T_{\mathrm{v}} & \text{if} \; T_{\mathrm{x}} = 0 \lor T_{\mathrm{x}} = 1 \\
  T_{\mathrm{g}}T_{\mathrm{m}} + T_{\mathrm{v}} & \text{if} \; T_{\mathrm{x}} = 2 \\
  \end{cases} \qquad \text{(68)}
```

妥当性は次のように判定される。

<span id="eq-69"></span><span id="transaction_nonce"></span>

```math
\begin{array}{rcl}
S(T) & \neq & \varnothing \quad \wedge \\
\boldsymbol{\sigma}[S(T)]_{\mathrm{c}} & = & \texttt{KEC}\big( () \big) \quad \wedge \\
T_{\mathrm{n}} & = & \boldsymbol{\sigma}[S(T)]_{\mathrm{n}} \quad \wedge \\
g_0 & \leqslant & T_{\mathrm{g}} \quad \wedge \\
v_0 & \leqslant & \boldsymbol{\sigma}[S(T)]_{\mathrm{b}} \quad \wedge \\
m & \geqslant & H_{\mathrm{f}} \quad \wedge \\
n & \leqslant & 49152 \quad \wedge \\
T_{\mathrm{g}} & \leqslant & {B_{\mathrm{H}}}_{\mathrm{l}} - \ell(B_{\mathbf{R}})_{\mathrm{u}}
\end{array} \qquad \text{(69)}
```

ここで、

<span id="eq-70"></span>

```math
m \equiv \begin{cases}
  T_{\mathrm{p}} & \text{if} \; T_{\mathrm{x}} = 0 \lor T_{\mathrm{x}} = 1 \\
  T_{\mathrm{m}} & \text{if} \; T_{\mathrm{x}} = 2 \\
  \end{cases} \qquad \text{(70)}
```

かつ、

<span id="eq-71"></span>

```math
n \equiv \begin{cases}
    \lVert T_{\mathrm{i}} \rVert & \text{if} \; T_{\mathrm{t}} = \varnothing \\
    0 & \text{otherwise}
  \end{cases} \qquad \text{(71)}
```

最後から二番目の条件は、作成トランザクションについてinitcodeの長さが49152バイト以下であることを保証する。最後の条件にも注意されたい。トランザクションのgas上限 $`T_{\mathrm{g}}`$ と、それ以前にこのブロックで使用されたgas $`\ell(B_{\mathbf{R}})_{\mathrm{u}}`$ の和は、ブロックの **gasLimit** $`{B_{\mathrm{H}}}_{\mathrm{l}}`$ 以下でなければならない。また、記法をわずかに濫用して、 $`\boldsymbol{\sigma}[S(T)] = \varnothing`$ の場合には $`\boldsymbol{\sigma}[S(T)]_{\mathrm{c}} = \texttt{KEC}\big( () \big)`$ 、 $`\boldsymbol{\sigma}[S(T)]_{\mathrm{n}} = 0`$ 、 $`\boldsymbol{\sigma}[S(T)]_{\mathrm{b}} = 0`$ と仮定する。

型2トランザクションについては、**maxPriorityFeePerGas** が **maxFeePerGas** 以下であるという追加検査を行う。

<span id="eq-72"></span>

```math
T_{\mathrm{m}} \geqslant T_{\mathrm{f}} \qquad \text{(72)}
```

妥当なトランザクションの実行は、状態への取消不能な変更から始まる。送信者アカウント $`S(T)`$ の[nonce](04-blocks-state-transactions.md#account_nonce)を1増加させ、残高から前払いコストの一部 $`T_{\mathrm{g}} p`$ を減じる。後続の計算に利用できるgas $`g`$ は $`T_{\mathrm{g}} - g_0`$ と定義される。コントラクト作成かメッセージ呼び出しかを問わず、計算は最終的な状態（現在状態と同値でも正当である）をもたらす。この状態変更は決定論的であり、決して無効にはならない。この時点以降、無効なトランザクションは存在し得ない。

チェックポイント状態 $`\boldsymbol{\sigma}_0`$ を次のように定義する。

<span id="eq-73"></span><span id="eq-74"></span><span id="eq-75"></span>

```math
\begin{aligned}
\boldsymbol{\sigma}_0 & \equiv & \boldsymbol{\sigma} \quad \text{except:} & \qquad \text{(73)} \\
\boldsymbol{\sigma}_0[S(T)]_{\mathrm{b}} & \equiv & \boldsymbol{\sigma}[S(T)]_{\mathrm{b}} - T_{\mathrm{g}} p & \qquad \text{(74)} \\
\boldsymbol{\sigma}_0[S(T)]_{\mathrm{n}} & \equiv & \boldsymbol{\sigma}[S(T)]_{\mathrm{n}} + 1 & \qquad \text{(75)}
\end{aligned}
```

$`\boldsymbol{\sigma}_0`$ から $`\boldsymbol{\sigma}_{\mathrm{P}}`$ を評価する方法は、コントラクト作成かメッセージ呼び出しかというトランザクション型に依存する。実行後の暫定状態 $`\boldsymbol{\sigma}_{\mathrm{P}}`$ 、残存gas $`g'`$ 、累積サブ状態 $`A`$ 、ステータス・コード $`z`$ のタプルを次のように定義する。

<span id="eq-76"></span>

```math
(\boldsymbol{\sigma}_{\mathrm{P}}, g', A, z) \equiv \begin{cases}
\Lambda_{4}(\boldsymbol{\sigma}_0, A^{*}, S(T), S(T), g, &\\ \quad\; p, T_{\mathrm{v}}, T_{\mathbf{i}}, 0, \varnothing, \top) & \text{if} \quad T_{\mathrm{t}} = \varnothing \\
\Theta_{4}(\boldsymbol{\sigma}_0, A^{*}, S(T), S(T), T_{\mathrm{t}}, &\\ \quad\; T_{\mathrm{t}}, g, p, T_{\mathrm{v}}, T_{\mathrm{v}}, T_{\mathbf{d}}, 0, \top) & \text{otherwise}
\end{cases} \qquad \text{(76)}
```

ここで、

<span id="eq-77"></span><span id="eq-78"></span><span id="eq-79"></span><span id="eq-80"></span>

```math
\begin{aligned}
A^{*} & \equiv A^0 \quad \text{except} & \qquad \text{(77)} \\
A^{*}_{\mathbf{K}} & \equiv \bigcup_{E \in T_{\mathbf{A}}} \big\{ \forall i < \lVert E_{\mathbf{s}} \rVert, i \in \mathbb{N}: \; (E_{\mathrm{a}}, E_{\mathbf{s}}[i]) \big\} & \qquad \text{(78)} \\
A^{*}_{\mathbf{a}} & \equiv \begin{cases}
a \cup T_{\mathrm{t}} & \text{if} \quad T_{\mathrm{t}} \neq \varnothing \\
a & \text{otherwise}
\end{cases} & \qquad \text{(79)} \\
a & \equiv A^0_{\mathbf{a}} \cup S(T) \cup H_c \cup_{E \in T_{\mathbf{A}}} \{ E_{\mathrm{a}} \} & \qquad \text{(80)}
\end{aligned}
```

また $`g`$ は、トランザクションが存在するために支払う基本量を差し引いた後に残るgas量である。

<span id="eq-81"></span>

```math
g \equiv T_{\mathrm{g}} - g_0 \qquad \text{(81)}
```

$`\Theta_{4}`$ と $`\Lambda_{4}`$ は、関数値の最初の四つの構成要素だけを取ることを表すために用いている点に注意されたい。最後の構成要素はメッセージ呼び出しの出力値（バイト配列）を表し、トランザクション評価の文脈では使用されない。

次に、残存gas $`g'`$ と還付カウンタからの一定の割当てに基づき、元のレートで送信者へ還付する量 $`g^{*}`$ を決定して状態を最終化する。

<span id="eq-82"></span>

```math
g^{*} \equiv g' + \min \left\{ \Big\lfloor \dfrac{T_{\mathrm{g}} - g'}{5} \Big\rfloor, A_{\mathrm{r}} \right\} \qquad \text{(82)}
```

還付可能な総量は、正当に残ったgas $`g'`$ に $`A_{\mathrm{r}}`$[↗](#refund_balance_defn_words_A__r) を加えたものである。ただし後者は、総使用量 $`T_{\mathrm{g}} - g'`$ の最大5分の1[^9]（切り捨て）に制限される。したがって $`g^{*}`$ は、トランザクション実行後に残るgasの総量である。

現在のブロック $`B`$ の受益者としてアドレスが指定されたバリデータは、消費gas量に、この節で $`f`$[↗](#priority_fee_f) と定義するトランザクションの*gas当たり優先手数料*を掛けた額を受け取る。トランザクション送信者が支払うEtherのうち基本手数料に充てられる分は、そのアカウントから引き落とされるが、ほかのいかなるアカウントにも加算されないため、バーンされる。

最終化前状態 $`\boldsymbol{\sigma}^{*}`$ を暫定状態 $`\boldsymbol{\sigma}_{\mathrm{P}}`$ によって次のように定義する。

<span id="eq-83"></span><span id="eq-84"></span><span id="eq-85"></span>

```math
\begin{aligned}
\boldsymbol{\sigma}^{*} & \equiv & \boldsymbol{\sigma}_{\mathrm{P}} \quad \text{except} & \qquad \text{(83)} \\
\boldsymbol{\sigma}^{*}[S(T)]_{\mathrm{b}} & \equiv & \boldsymbol{\sigma}_{\mathrm{P}}[S(T)]_{\mathrm{b}} + g^{*} p & \qquad \text{(84)} \\
\boldsymbol{\sigma}^{*}[{B_{\mathrm{H}}}_{\mathrm{c}}]_{\mathrm{b}} & \equiv & \boldsymbol{\sigma}_{\mathrm{P}}[{B_{\mathrm{H}}}_{\mathrm{c}}]_{\mathrm{b}} + (T_{\mathrm{g}} - g^{*}) f & \qquad \text{(85)}
\end{aligned}
```

最終状態 $`\boldsymbol{\sigma}'`$ は、自己破棄集合に現れるか、接触済みかつ空であるすべてのアカウントを削除した後に得られる。

<span id="eq-86"></span><span id="eq-87"></span><span id="eq-88"></span>

```math
\begin{aligned}
\boldsymbol{\sigma}' & \equiv & \boldsymbol{\sigma}^{*} \quad \text{except} & \qquad \text{(86)} \\
\forall i \in A_{\mathbf{s}}: \boldsymbol{\sigma}'[i] & = & \varnothing & \qquad \text{(87)} \\
\forall i \in A_{\mathbf{t}}: \boldsymbol{\sigma}'[i] & = & \varnothing \quad\text{if}\quad \mathtt{DEAD}(\boldsymbol{\sigma}^{*}, i) & \qquad \text{(88)}
\end{aligned}
```

<div id="tx_total_gas_used_Upsilon_pow_g">

</div>

<span id="Upsilon_pow_l"></span>

<span id="tx_logs_Upsilon_pow_l"></span><span id="Upsilon_pow_z"></span>

<span id="tx_status_Upsilon_pow_z"></span>最後に、このトランザクションで使用された総gas $`\Upsilon^{\mathrm{g}}`$ 、このトランザクションが生成したログ $`\Upsilon^{\mathbf{l}}`$ 、およびトランザクションのステータス・コード $`\Upsilon^{\mathrm{z}}`$ を規定する。

<span id="eq-89"></span><span id="eq-90"></span><span id="eq-91"></span>

```math
\begin{aligned}
\Upsilon^{\mathrm{g}}(\boldsymbol{\sigma}, T) & \equiv & T_{\mathrm{g}} - g^{*} & \qquad \text{(89)} \\
\Upsilon^{\mathbf{l}}(\boldsymbol{\sigma}, T) & \equiv & A_{\mathbf{l}} & \qquad \text{(90)} \\
\Upsilon^{\mathrm{z}}(\boldsymbol{\sigma}, T) & \equiv & z & \qquad \text{(91)}
\end{aligned}
```

これらは[トランザクション・レシート](04-blocks-state-transactions.md#Transaction_Receipt)の定義に用いられ、さらに[後で](12-block-finalisation.md#sigma_n)状態検証にも用いられる。

[^9]: gasの最大還付割合は、*London* リリースにおいて[(Buterin and Swende 2021)](../references.md#ref-EIP-3529)によるEIP-3529で2分の1から5分の1へ引き下げられた。
