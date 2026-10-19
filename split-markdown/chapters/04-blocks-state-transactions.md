[分割版目次](../README.md) | [前へ](03-conventions.md) | [次へ](05-gas-and-payment.md) | [単一ページ版](../../ethereum_yellow_paper_ja.md)

<span id="ch:bst"></span>

# 4. ブロック、状態、トランザクション

Ethereum の基礎概念を導入したので、トランザクション、ブロック、状態の意味をさらに詳しく論じる。

<span id="ch:state"></span>

## 4.1. ワールド状態

ワールド状態（*状態*）は、アドレス（160ビット識別子）からアカウント状態（RLP として直列化されるデータ構造、[付録B](../appendices/appendix-b-rlp.md#app:rlp)参照）への写像である。ワールド状態自体はブロックチェーンに格納されないが、実装はこの写像を修正 Merkle Patricia 木（*トライ*、[付録D](../appendices/appendix-d-trie.md#app:trie)参照）で維持するものと仮定する。トライには、バイト配列からバイト配列への写像を維持する単純なデータベース・バックエンドが必要であり、この基盤データベースを状態データベースと呼ぶ。これにはいくつかの利点がある。第一に、この構造のルート・ノードは暗号学的にすべての内部データに依存するため、そのハッシュをシステム状態全体の安全な識別子として利用できる。第二に、不変データ構造であるため、ルート・ハッシュが既知の過去状態は、ルート・ハッシュを対応する値へ変更するだけで呼び戻せる。こうしたルート・ハッシュはすべてブロックチェーンに格納されるため、古い状態へ容易に戻せる。

アカウント状態 $`\boldsymbol{\sigma}[a]`$ は、次の4フィールドからなる。

<span id="account_nonce"></span>

nonce
: このアドレスから送信されたトランザクション数に等しいスカラー値。コードが関連付けられたアカウントの場合は、このアカウントが行ったコントラクト作成数に等しい。状態 $`\boldsymbol{\sigma}`$ におけるアドレス $`a`$ のアカウントについて、形式的には $`\boldsymbol{\sigma}[a]_{\mathrm{n}}`$ と表す。

balance
: このアドレスが所有する Wei の数量に等しいスカラー値。形式的には $`\boldsymbol{\sigma}[a]_{\mathrm{b}}`$ と表す。

storageRoot
: アカウントのストレージ内容（256ビット整数値間の写像）を符号化する Merkle Patricia 木のルート・ノードの256ビット・ハッシュ。これは、256ビット整数キーの Keccak 256ビット・ハッシュから、RLP 符号化された256ビット整数値への写像としてトライに符号化される。このハッシュを形式的には $`\boldsymbol{\sigma}[a]_{\mathrm{s}}`$ と表す。

codeHash
: このアカウントの EVM コードのハッシュ。このアドレスがメッセージ呼び出しを受けると、このコードが実行される。このようなコード断片はすべて、後で取得できるよう対応するハッシュの下で状態データベースに格納される。このハッシュを形式的には $`\boldsymbol{\sigma}[a]_{\mathrm{c}}`$ と表す。したがって、 $`\texttt{KEC}(\mathbf{b}) = \boldsymbol{\sigma}[a]_{\mathrm{c}}`$ となるコードを $`\mathbf{b}`$ と表せる。

通常参照したいのはトライのルート・ハッシュではなく、内部に格納されたキー／値ペアの集合であるため、次の便利な同値関係を定義する。

<span id="eq-7"></span>

```math
\texttt{TRIE}\big(L_{\mathrm{I}}^{*}(\boldsymbol{\sigma}[a]_{\mathbf{s}})\big) \equiv \boldsymbol{\sigma}[a]_{\mathrm{s}} \qquad \text{(7)}
```

トライ内のキー／値ペア集合に対する縮約関数 $`L_{\mathrm{I}}^{*}`$ は、次に示す基礎関数 $`L_{\mathrm{I}}`$ を要素ごとに適用する変換として定義される。

<span id="eq-8"></span>

```math
L_{\mathrm{I}}\big( (k, v) \big) \equiv \big(\texttt{KEC}(k), \texttt{RLP}(v)\big) \qquad \text{(8)}
```

ここで、

<span id="eq-9"></span>

```math
k \in \mathbb{B}_{32} \quad \wedge \quad v \in \mathbb{N} \qquad \text{(9)}
```

$`\boldsymbol{\sigma}[a]_{\mathbf{s}}`$ はアカウントの「物理的」な構成要素ではなく、後の直列化には寄与しないものと理解されたい。

**codeHash** フィールドが空文字列の Keccak-256 ハッシュ、すなわち $`\boldsymbol{\sigma}[a]_{\mathrm{c}} = \texttt{KEC}\big(()\big)`$ であれば、そのノードは単純アカウントを表し、「非コントラクト」アカウントと呼ばれることもある。

したがって、ワールド状態の縮約関数 $`L_{\mathrm{S}}`$ を次のように定義できる。

<span id="eq-10"></span>

```math
L_{\mathrm{S}}(\boldsymbol{\sigma}) \equiv \{ p(a): \boldsymbol{\sigma}[a] \neq \varnothing \} \qquad \text{(10)}
```

ここで、

<span id="eq-11"></span>

```math
p(a) \equiv  \big(\texttt{KEC}(a), \texttt{RLP}\big( (\boldsymbol{\sigma}[a]_{\mathrm{n}}, \boldsymbol{\sigma}[a]_{\mathrm{b}}, \boldsymbol{\sigma}[a]_{\mathrm{s}}, \boldsymbol{\sigma}[a]_{\mathrm{c}}) \big) \big) \qquad \text{(11)}
```

である。

この関数 $`L_{\mathrm{S}}`$ はトライ関数とともに用いられ、ワールド状態の短い識別子（ハッシュ）を与える。次を仮定する。

<span id="eq-12"></span>

```math
\forall a: \boldsymbol{\sigma}[a] = \varnothing \; \vee \; (a \in \mathbb{B}_{20} \; \wedge \; v(\boldsymbol{\sigma}[a])) \qquad \text{(12)}
```

ここで $`v`$ はアカウント妥当性関数である。

<span id="eq-13"></span>

```math
\quad v(x) \equiv x_{\mathrm{n}} \in \mathbb{N}_{256} \wedge x_{\mathrm{b}} \in \mathbb{N}_{256} \wedge x_{\mathrm{s}} \in \mathbb{B}_{32} \wedge x_{\mathrm{c}} \in \mathbb{B}_{32} \qquad \text{(13)}
```

コードを持たず、nonceと残高がともにゼロであるとき、アカウントは*空（empty）*である。

<span id="eq-14"></span>

```math
\mathtt{EMPTY}(\boldsymbol{\sigma}, a) \quad\equiv\quad \boldsymbol{\sigma}[a]_{\mathrm{c}} = \texttt{KEC}\big(()\big) \wedge \boldsymbol{\sigma}[a]_{\mathrm{n}} = 0 \wedge \boldsymbol{\sigma}[a]_{\mathrm{b}} = 0 \qquad \text{(14)}
```

呼び出し可能なプリコンパイル済みコントラクトであっても、アカウント状態が空であり得る。これは通常、その振る舞いを記述するコードがアカウント状態に含まれないためである。

アカウント状態が存在しないか空であるとき、そのアカウントは*死んでいる（dead）*という。

<span id="eq-15"></span>

```math
\mathtt{DEAD}(\boldsymbol{\sigma}, a) \quad\equiv\quad \boldsymbol{\sigma}[a] = \varnothing \vee \mathtt{EMPTY}(\boldsymbol{\sigma}, a) \qquad \text{(15)}
```

<span id="subsec:transaction"></span>

## 4.2. トランザクション

トランザクション（形式的には $`T`$ ）は、Ethereum の範囲外にいる主体が作成する、暗号学的に署名された一つの命令である。トランザクションの送信者をコントラクトとすることはできない。最終的な外部主体は人間であると仮定するが、トランザクションの作成と配布にはソフトウェア・ツールが用いられる[^3]。[(Zoltu 2020)](../references.md#ref-EIP-2718) の EIP-2718 は異なるトランザクション型という概念を導入した。プロトコルの *London* 版時点で、トランザクション型は0（レガシー）、1（[(Buterin and Swende 2020b)](../references.md#ref-EIP-2930) の EIP-2930）、2（[(Buterin et al. 2019)](../references.md#ref-EIP-1559) の EIP-1559）の3種類である。さらに、トランザクションには、メッセージ呼び出しをもたらすものと、コードが関連付けられた新しいアカウントを作成するもの（非形式的には「コントラクト作成」と呼ばれる）の二つの下位型がある。すべてのトランザクション型は、次の共通フィールドを指定する。

<span id="tx_type"></span>

type
: EIP-2718 トランザクション型。形式的には $`T_{\mathrm{x}}`$ 。

nonce
: 送信者が送信したトランザクション数に等しいスカラー値。形式的には $`T_{\mathrm{n}}`$ 。

gasLimit
: このトランザクションの実行に使用できる gas の最大量に等しいスカラー値。これは計算を行う前に前払いされ、後から増やすことはできない。形式的には $`T_{\mathrm{g}}`$ 。

to
: メッセージ呼び出しの受信者の160ビット・アドレス。コントラクト作成トランザクションの場合は、ここでは $`\mathbb{B}_0`$ の唯一の要素を表す $`\varnothing`$ 。形式的には $`T_{\mathrm{t}}`$ 。

value
: メッセージ呼び出しの受信者へ移転する Wei の数量、またはコントラクト作成の場合は新たに作成されるアカウントへ付与する Wei の数量に等しいスカラー値。形式的には $`T_{\mathrm{v}}`$ 。

<span id="T__r_T__s"></span>

r, s
: トランザクションの署名に対応し、その送信者を決定するために用いる値。形式的には $`T_{\mathrm{r}}`$ と $`T_{\mathrm{s}}`$ 。[付録F](../appendices/appendix-f-signing-transactions.md#app:signing)で詳述する。

EIP-2930（型1）および EIP-1559（型2）トランザクションは、さらに次のフィールドを持つ。

accessList
: ウォームアップするアクセス項目のリスト。形式的には $`T_{\mathbf{A}}`$ 。各アクセス・リスト項目 $`E`$ は、アカウント・アドレスとストレージ・キーのリストとのタプルである： $`E \equiv (E_{\mathrm{a}}, E_{\mathbf{s}})`$ 。

chainId
: チェーンID。形式的には $`T_{\mathrm{c}}`$ 。ネットワークのチェーンID $`\beta`$[↗](02-blockchain-paradigm.md#chain_id) と等しくなければならない。

yParity
: 署名の Y パリティ。形式的には $`T_{\mathrm{y}}`$ 。

レガシー・トランザクションは **accessList** を持たず（ $`T_{\mathbf{A}}=()`$ ）、レガシー・トランザクションの **chainId** と **yParity** は一つの値に結合される。

w
: Y パリティと、場合によってはチェーンIDを符号化するスカラー値。形式的には $`T_{\mathrm{w}}`$ 。 $`T_{\mathrm{w}} = 27 + T_{\mathrm{y}}`$ または $`T_{\mathrm{w}} = 2\beta + 35 + T_{\mathrm{y}}`$ （[(Buterin 2016)](../references.md#ref-EIP-155) の EIP-155 参照）。

許容する gas 価格の指定方法は、型2と、型0および型1のトランザクションとで異なる。型2トランザクションは、支払う*優先手数料*[^4]を明示的に制限することで、EIP-1559 が導入した gas 市場の改善をより活用する。型2トランザクションは gas に関する次の二つのフィールドを持つ。

maxFeePerGas
: このトランザクションの実行によって生じるすべての計算コストについて、*gas* 1単位当たりに支払う Wei の最大量に等しいスカラー値。形式的には $`T_{\mathrm{m}}`$ 。

maxPriorityFeePerGas
: トランザクションを収録するインセンティブとして、ブロックの手数料受取人に支払う Wei の最大量に等しいスカラー値。形式的には $`T_{\mathrm{f}}`$ 。

これに対し、型0および型1トランザクションは gas 価格を単一の値として指定する。

gasPrice
: このトランザクションの実行によって生じるすべての計算コストについて、*gas* 1単位当たりに支払う Wei の数量に等しいスカラー値。形式的には $`T_{\mathrm{p}}`$ [^5]。

さらに、コントラクト作成トランザクションは（トランザクション型にかかわらず）次を含む。

init
: アカウント初期化手続きの EVM コードを指定する、サイズ無制限のバイト配列。形式的には $`T_{\mathbf{i}}`$ 。

<span id="tnref-1"></span>[訳注1](../translation-notes.md#tn-1)

**init** は EVM コード断片であり、**body** を返す。**body** は、そのアカウントがメッセージ呼び出しを受けるたびに（トランザクションを介する場合も、コードの内部実行による場合も）実行される第2のコード断片である。**init** はアカウント作成時に一度だけ実行され、その直後に破棄される。

これに対し、メッセージ呼び出しトランザクションは次を含む。

data
: メッセージ呼び出しの入力データを指定する、サイズ無制限のバイト配列。形式的には $`T_{\mathbf{d}}`$ 。

[付録F](../appendices/appendix-f-signing-transactions.md#app:signing)では、トランザクションを送信者へ写像する関数 $`S`$ を規定する。この写像は SECP-256k1 曲線の ECDSA により、後ろの三つの署名フィールドを除いたトランザクションのハッシュを署名対象データとして用いて行われる。ここでは、所与のトランザクション $`T`$ の送信者を $`S(T)`$ で表せるとだけ仮定する。

<span id="eq-16"></span>

```math
L_{\mathrm{T}}(T) \equiv \begin{cases}
(T_{\mathrm{n}}, T_{\mathrm{p}}, T_{\mathrm{g}}, T_{\mathrm{t}}, T_{\mathrm{v}}, \mathbf{p}, T_{\mathrm{w}}, T_{\mathrm{r}}, T_{\mathrm{s}}) & \text{if} \; T_{\mathrm{x}} = 0 \\
(T_{\mathrm{c}}, T_{\mathrm{n}}, T_{\mathrm{p}}, T_{\mathrm{g}}, T_{\mathrm{t}}, T_{\mathrm{v}}, \mathbf{p}, T_{\mathbf{A}}, T_{\mathrm{y}}, T_{\mathrm{r}}, T_{\mathrm{s}}) & \text{if} \; T_{\mathrm{x}} = 1 \\
(T_{\mathrm{c}}, T_{\mathrm{n}}, T_{\mathrm{f}}, T_{\mathrm{m}}, T_{\mathrm{g}}, T_{\mathrm{t}}, T_{\mathrm{v}}, \mathbf{p}, T_{\mathbf{A}}, T_{\mathrm{y}}, T_{\mathrm{r}}, T_{\mathrm{s}}) & \text{if} \; T_{\mathrm{x}} = 2 \\
\end{cases} \qquad \text{(16)}
```

ここで、

<span id="eq-17"></span>

```math
\mathbf{p} \equiv \begin{cases}
T_{\mathbf{i}} & \text{if}\ T_{\mathrm{t}} = \varnothing \\
T_{\mathbf{d}} & \text{otherwise}
\end{cases} \qquad \text{(17)}
```

ここで、アクセス・リスト $`T_{\mathbf{A}}`$ と任意長のバイト配列 $`T_{\mathbf{i}}`$ および $`T_{\mathbf{d}}`$ を除き、すべての構成要素はRLPによって整数値として解釈されるものとする。

<span id="eq-18"></span>

```math
\begin{array}{lclclc}
T_{\mathrm{x}} \in \{0, 1, 2\} & \wedge & T_{\mathrm{c}} = \beta & \wedge & T_{\mathrm{n}} \in \mathbb{N}_{256} & \wedge \\
T_{\mathrm{p}} \in \mathbb{N}_{256} & \wedge & T_{\mathrm{g}} \in \mathbb{N}_{256} & \wedge & T_{\mathrm{v}} \in \mathbb{N}_{256} & \wedge \\
T_{\mathrm{w}} \in \mathbb{N}_{256} & \wedge & T_{\mathrm{r}} \in \mathbb{N}_{256} & \wedge & T_{\mathrm{s}} \in \mathbb{N}_{256} & \wedge \\
T_{\mathrm{y}} \in \mathbb{N}_{1} & \wedge & T_{\mathbf{d}} \in \mathbb{B} & \wedge & T_{\mathbf{i}} \in \mathbb{B} & \wedge \\
T_{\mathrm{m}} \in \mathbb{N}_{256} & \wedge & T_{\mathrm{f}} \in \mathbb{N}_{256}
\end{array} \qquad \text{(18)}
```

ここで、

<span id="eq-19"></span>

```math
\mathbb{N}_{\mathrm{n}} = \{ P: P \in \mathbb{N} \wedge P < 2^n \} \qquad \text{(19)}
```

アドレス・ハッシュ $`T_{\mathbf{t}}`$ はやや異なる。これは20バイトのアドレス・ハッシュであるか、コントラクト作成トランザクションの場合（したがって形式的には $`\varnothing`$ に等しい）はRLPの空バイト列、すなわち $`\mathbb{B}_0`$ の要素となる。

<span id="eq-20"></span>

```math
T_{\mathbf{t}} \in \begin{cases} \mathbb{B}_{20} & \text{if} \quad T_{\mathrm{t}} \neq \varnothing \\
\mathbb{B}_{0} & \text{otherwise}\end{cases} \qquad \text{(20)}
```

<span id="subsec:The_Withdrawal"></span>

## 4.3. 引き出し

引き出し（形式的には *W*）は、合意レイヤーのバリデータがステーク済みEtherの一部を引き出すことを記述するデータのタプルである。引き出しはブロックチェーンの合意レイヤーで作成・検証された後、実行レイヤーへ送られる。引き出しは次のフィールドから構成される。

globalIndex
: ゼロから始まり単調に増加する引き出しインデックスであり、この引き出しの一意な識別子として機能する。形式的には $`W_{\mathrm{g}}`$ 。

validatorIndex
: この引き出しに対応する合意レイヤーのバリデータのインデックス。形式的には $`W_{\mathrm{v}}`$ 。

recipient
: この引き出しによるEtherを受け取る20バイトのアドレス。形式的には $`W_{\mathrm{r}}`$ 。

amount
: Gwei（ $`10^9`$ Wei）単位で表したゼロではないEther量。形式的には $`W_{\mathrm{a}}`$ 。

引き出しの直列化を次のように定義する。

<span id="eq-21"></span>

```math
L_{\mathrm{W}}(W) \equiv
(W_{\mathrm{g}}, W_{\mathrm{v}}, W_{\mathrm{r}}, T_{\mathrm{a}}) \qquad \text{(21)}
```

<span id="tnref-2"></span>[訳注2](../translation-notes.md#tn-2)

ここで、20バイトのアドレスである $`W_\mathbf{r}`$ を除き、すべての構成要素はRLPによって整数値として解釈されるものとする。

<span id="eq-22"></span>

```math
\begin{array}{lclc}
W_{\mathrm{g}} \in \mathbb{N}_{64} & \wedge & W_{\mathrm{v}} \in \mathbb{N}_{64} & \wedge \\
W_{\mathrm{r}} \in \mathbb{B}_{20} & \wedge & W_{\mathrm{a}} \in \mathbb{N}_{64}
\end{array} \qquad \text{(22)}
```

<span id="subsec:The_Block"></span>

<span id="block"></span>

## 4.4. ブロック

Ethereumのブロックは、関連情報の集合（ブロック*ヘッダ*と呼ばれる） $`H`$ と、そこに含まれるトランザクションに対応する情報 $`\mathbf{T}`$ 、<span id="ommerheaders"></span>現在は非推奨となった属性 $`\mathbf{U}`$ 、および *Shanghai* ハードフォーク以降は合意レイヤーから送られるバリデータ引き出しの集合 $`\mathbf{W}`$ からなる。 $`\mathbf{U}`$ には *Paris* ハードフォーク以前、親が現在のブロックの親の親と等しいブロック（このようなブロックは*ommer*[^6]と呼ばれた）のヘッダが含まれていた。ブロック・ヘッダは次の情報を含む。

parentHash
: 親ブロックのヘッダ全体のKeccak 256ビット・ハッシュ。形式的には $`H_{\mathrm{p}}`$ 。

ommersHash
: プルーフ・オブ・ワーク合意の置換により現在は非推奨となった256ビットのハッシュ・フィールド。現在は定数 $`\texttt{KEC}(\texttt{RLP}(()))`$ である。形式的には $`H_{\mathrm{o}}`$ 。

beneficiary
: このブロックの優先手数料が送金される160ビットのアドレス。形式的には $`H_{\mathrm{c}}`$ 。

stateRoot
: すべてのトランザクションと引き出しを実行し、最終化を適用した後の状態トライのルート・ノードのKeccak 256ビット・ハッシュ。形式的には $`H_{\mathrm{r}}`$ 。

transactionsRoot
: ブロックのトランザクション・リスト部分にある各トランザクションを格納したトライ構造のルート・ノードのKeccak 256ビット・ハッシュ。形式的には $`H_{\mathrm{t}}`$ 。

receiptsRoot
: ブロックのトランザクション・リスト部分にある各トランザクションのレシートを格納したトライ構造のルート・ノードのKeccak 256ビット・ハッシュ。形式的には $`H_{\mathrm{e}}`$ 。

logsBloom
: トランザクション・リスト内の各トランザクションのレシートにある各ログ項目に含まれる、索引付け可能な情報（ロガーのアドレスとログ・トピック）から構成されるBloomフィルタ。形式的には $`H_{\mathrm{b}}`$ 。

difficulty
: プルーフ・オブ・ワーク合意の置換により現在は非推奨となったスカラー・フィールド。0に設定される。形式的には $`H_{\mathrm{d}}`$ 。

number
: 祖先ブロック数に等しいスカラー値。ジェネシス・ブロックの値は0である。形式的には $`H_{\mathrm{i}}`$[↗](#block_number_H__i)。

gasLimit
: ブロック当たりの現在のgas消費上限に等しいスカラー値。形式的には $`H_{\mathrm{l}}`$ 。

<span id="H__g"></span>

gasUsed
: このブロックのトランザクションで使用されたgasの総量に等しいスカラー値。形式的には $`H_{\mathrm{g}}`$ 。

timestamp
: このブロックの生成時点におけるUnixの `time()` の妥当な出力に等しいスカラー値。形式的には $`H_{\mathrm{s}}`$[↗](#block_timestamp_H__s)。

extraData
: このブロックに関連するデータを含む任意のバイト配列。32バイト以下でなければならない。形式的には $`H_{\mathrm{x}}`$ 。

prevRandao
: 直前のブロックを処理した後のビーコン状態における最新のRANDAO mix[^7]。形式的には $`H_{\mathrm{a}}`$ 。

<span id="H__n"></span>

nonce
: プルーフ・オブ・ワーク合意の置換により現在は非推奨となった64ビット値。`0x0000000000000000` に設定される。形式的には $`H_{\mathrm{n}}`$[↗](#H__n)。

<span id="block_baseFeePerGas_H__f"></span>

baseFeePerGas
: 消費されるgas 1単位ごとにバーンされるwei量に等しいスカラー値。形式的には $`H_{\mathrm{f}}`$[↗](#H__f)。

<span id="H__w"></span>

withdrawalsRoot
: このブロックについて合意レイヤーから送られた各引き出し操作を格納したトライ構造のルート・ノードのKeccak 256ビット・ハッシュ。形式的には $`H_{\mathrm{w}}`$[↗](#H__w)。

ブロックの残る三つの構成要素は、トランザクション列 $`B_{\mathbf{T}}`$ 、以前ommerブロック・ヘッダ用に予約されていた空配列 $`B_{\mathbf{U}}`$ 、および引き出し列 $`B_{\mathbf{W}}`$ である。形式的にはブロック $`B`$ を次のように表す。

<span id="eq-23"></span>

```math
B \equiv (B_{\mathrm{H}}, B_{\mathbf{T}}, B_{\mathbf{U}}, B_{\mathbf{W}}) \qquad \text{(23)}
```

<span id="Transaction_Receipt"></span>

### 4.4.1. トランザクション・レシート

ゼロ知識証明の構成、索引付け、検索に有用となり得るトランザクション情報を符号化するため、実行によって得られる一定の情報を含むレシートを各トランザクションについて符号化する。第 $`i`$ トランザクションのレシートを $`B_{\mathbf{R}}[i]`$ と表し、インデックスをキーとする[トライ](../appendices/appendix-d-trie.md#trie)に格納する。そのルートはヘッダに $`H_{\mathrm{e}}`$[↗](#Receipts_Root_H__e) として記録される。

トランザクション・レシート $`R`$ は五つの要素からなるタプルである。すなわち、トランザクションの型 $`R_{\mathrm{x}}`$ 、ステータス・コード $`R_{\mathrm{z}}`$ 、そのトランザクションが生じた直後の時点で当該レシートを含むブロック内において使用済みの累積gas $`R_{\mathrm{u}}`$ 、トランザクションの実行によって生成されたログ集合 $`R_\mathbf{l}`$[↗](../appendices/appendix-b-rlp.md#RLP_serialisation_of_a_sequence_of_other_items_R__l_math_def)、およびそれらのログ情報から構成されるBloomフィルタ $`R_{\mathrm{b}}`$[↗](../appendices/appendix-b-rlp.md#RLP_serialisation_of_a_byte_array_R__b_math_def) である。

<span id="eq-24"></span>

```math
R \equiv (R_{\mathrm{x}}, R_{\mathrm{z}}, R_{\mathrm{u}}, R_{\mathrm{b}}, R_{\mathbf{l}}) \qquad \text{(24)}
```

$`R_{\mathrm{x}}`$ は対応するトランザクションの[型](#tx_type)に等しい。

関数 $`L_{\mathrm{R}}`$ は、トランザクション・レシートをRLP直列化されたバイト配列へ変換するために準備する。

<span id="eq-25"></span>

```math
L_{\mathrm{R}}(R) \equiv (R_{\mathrm{z}}, R_{\mathrm{u}}, R_{\mathrm{b}}, R_{\mathbf{l}}) \qquad \text{(25)}
```

ステータス・コード $`R_{\mathrm{z}}`$ は非負整数である。

<span id="eq-26"></span>

```math
R_{\mathrm{z}} \in \mathbb{N} \qquad \text{(26)}
```

累積使用gas $`R_{\mathrm{u}}`$ は非負整数であり、ログBloom $`R_{\mathrm{b}}`$ は2048ビット（256バイト）のハッシュである。

<span id="eq-27"></span>

```math
R_{\mathrm{u}} \in \mathbb{N} \quad \wedge \quad R_{\mathrm{b}} \in \mathbb{B}_{256} \qquad \text{(27)}
```

列 $`R_{\mathbf{l}}`$ はログ項目の列 $`(O_0, O_1, ...)`$ である。ログ項目 $`O`$ は、ロガーのアドレス $`O_a`$ 、空でもよい32バイトのログ・トピック列 $`O_{\mathbf{t}}`$ 、および任意バイト数のデータ $`O_{\mathbf{d}}`$ からなるタプルである。

<span id="eq-28"></span>

```math
O \equiv (O_{\mathrm{a}}, ({O_{\mathbf{t}}}_0, {O_{\mathbf{t}}}_1, ...), O_{\mathbf{d}}) \qquad \text{(28)}
```

<span id="eq-29"></span>

```math
O_{\mathrm{a}} \in \mathbb{B}_{20} \quad \wedge \quad \forall x \in O_{\mathbf{t}}: x \in \mathbb{B}_{32} \quad \wedge \quad O_{\mathbf{d}} \in \mathbb{B} \qquad \text{(29)}
```

ログ項目を単一の256バイト・ハッシュへ縮約するBloomフィルタ関数 $`M`$ を次のように定義する。

<span id="eq-30"></span>

```math
M(O) \equiv \bigvee_{x \in \{O_{\mathrm{a}}\} \cup O_{\mathbf{t}}} \big( M_{3:2048}(x) \big) \qquad \text{(30)}
```

ここで $`M_{3:2048}`$ は、任意のバイト列を受け取り2048ビット中の3ビットを設定する専用Bloomフィルタである。これは、バイト列のKeccak-256ハッシュについて、先頭から三つの各2バイト対の下位11ビットを取ることで行われる。[^8] 形式的には次のとおりである。

<span id="eq-31"></span><span id="eq-32"></span><span id="eq-33"></span><span id="eq-34"></span>

```math
\begin{aligned}
M_{3:2048}(\mathbf{x}: \mathbf{x} \in \mathbb{B}) & \equiv & \mathbf{y}: \mathbf{y} \in \mathbb{B}_{256} \quad \text{where:} & \qquad \text{(31)} \\
\mathbf{y} & = & (0, 0, ..., 0) \quad \text{except:} & \qquad \text{(32)} \\
\forall i \in \{0, 2, 4\}&:&\mathcal{B}_{2047 - m(\mathbf{x}, i)}(\mathbf{y}) = 1 & \qquad \text{(33)} \\
m(\mathbf{x}, i) &\equiv& \mathtt{KEC}(\mathbf{x})[i, i + 1] \bmod 2048 & \qquad \text{(34)}
\end{aligned}
```

ここで $`\mathcal{B}`$ はビット参照関数であり、 $`\mathcal{B}_{\mathrm{j}}(\mathbf{x})`$ はバイト配列 $`\mathbf{x}`$ のインデックス $`j`$ （0始まり）のビットに等しい。特に、これは $`\mathbf{x}`$ をビッグエンディアンとして扱う（上位ビットほど小さいインデックスを持つ）。

### 4.4.2. 全体的妥当性

ブロックが妥当であるのは、次の諸条件を満たす場合、かつその場合に限る。ブロックのommerフィールド $`B_{\mathbf{U}}`$ は空配列でなければならず、ブロック・ヘッダは与えられたトランザクション $`B_{\mathbf{T}}`$ および引き出し $`B_{\mathbf{W}}`$ と整合しなければならない。ヘッダがトランザクション $`B_{\mathbf{T}}`$ および引き出し $`B_{\mathbf{W}}`$ と整合するには、**stateRoot** ( $`H_{\mathrm{r}}`$ ) が基底状態 $`\boldsymbol{\sigma}`$ 上で全トランザクション、次いで全引き出しを順に実行した結果の状態（[第12節](12-block-finalisation.md#ch:finalisation)で規定）と一致しなければならない。また、**transactionsRoot** ( $`H_{\mathrm{t}}`$ )、**receiptsRoot** ( $`H_{\mathrm{e}}`$ )、**logsBloom** ( $`H_{\mathrm{b}}`$ )、**withdrawalsRoot** ( $`H_{\mathrm{w}}`$ ) は、それぞれトランザクション自体、実行から得られるトランザクション・レシート、結果のログ、および引き出しから正しく導出されなければならない。

<span id="eq-35"></span><span id="Receipts_Root_H__e"></span>

```math
\begin{aligned}
B_{\mathbf{U}} &\equiv () && \wedge \\
H_{\mathrm{r}} &\equiv \mathtt{TRIE}(L_S(\Pi(\boldsymbol{\sigma}, B))) && \wedge \\
H_{\mathrm{t}} &\equiv \mathtt{TRIE}\big(\{\forall i < \lVert B_{\mathbf{T}} \rVert,
  i \in \mathbb{N}: p_{\mathrm{T}}(i, B_{\mathbf{T}}[i])\}\big) && \wedge \\
H_{\mathrm{e}} &\equiv \mathtt{TRIE}\big(\{\forall i < \lVert B_{\mathbf{R}} \rVert,
  i \in \mathbb{N}: p_{\mathrm{R}}(i, B_{\mathbf{R}}[i])\}\big) && \wedge \\
H_{\mathrm{w}} &\equiv \mathtt{TRIE}\big(\{\forall i < \lVert B_{\mathbf{W}} \rVert,
  i \in \mathbb{N}: p_{\mathrm{W}}(i, B_{\mathbf{W}}[i])\}\big) && \wedge \\
H_{\mathrm{b}} &\equiv \bigvee_{\mathbf{r} \in B_{\mathbf{R}}} \big(\mathbf{r}_{\mathrm{b}}\big)
\end{aligned} \qquad \text{(35)}
```

ここで $`p_{\mathrm{W}}(k, v)`$ は引き出しに対するペア単位のRLP変換である。

<span id="eq-36"></span>

```math
p_{\mathrm{W}}(k, W) \equiv \left( \mathtt{RLP}(k), \mathtt{RLP}(L_{\mathrm{W}}(W)) \right) \qquad \text{(36)}
```

同様に、 $`p_{\mathrm{T}}(k, v)`$ と $`p_{\mathrm{R}}(k, v)`$ もペア単位のRLP変換であるが、EIP-2718トランザクションを特別に扱う。

<span id="eq-37"></span>

```math
p_{\mathrm{T}}(k, T) \equiv \left( \mathtt{RLP}(k), \begin{cases}
\mathtt{RLP}(L_{\mathrm{T}}(T)) & \text{if} \quad T_{\mathrm{x}} = 0 \\
(T_{\mathrm{x}}) \cdot \mathtt{RLP}(L_{\mathrm{T}}(T)) & \text{otherwise}
\end{cases}
\right) \qquad \text{(37)}
```

また、

<span id="eq-38"></span>

```math
p_{\mathrm{R}}(k, R) \equiv \left( \mathtt{RLP}(k), \begin{cases}
\mathtt{RLP}(L_{\mathrm{R}}(R)) & \text{if} \quad R_{\mathrm{x}} = 0 \\
(R_{\mathrm{x}}) \cdot \mathtt{RLP}(L_{\mathrm{R}}(R)) & \text{otherwise}
\end{cases}
\right) \qquad \text{(38)}
```

（ $`\cdot`$ はバイト配列の連結である）。

さらに、次が成り立つ。

<span id="eq-39"></span>

```math
\mathtt{TRIE}(L_{\mathrm{S}}(\boldsymbol{\sigma})) = {P(B_H)_H}_{\mathrm{r}} \qquad \text{(39)}
```

したがって $`\texttt{TRIE}(L_{\mathrm{S}}(\boldsymbol{\sigma}))`$ は、値をRLPで符号化した状態 $`\boldsymbol{\sigma}`$ のキー／値ペアを含むMerkle Patricia木構造のルート・ノード・ハッシュである。また $`P(B_{\mathrm{H}})`$ は、直接定義される $`B`$ の親ブロックである。

トランザクション計算から生じる値、特に[トランザクション・レシート](#Transaction_Receipt) $`B_{\mathbf{R}}`$ と、トランザクションの[状態累積関数 $`\Pi`$](12-block-finalisation.md#Pi) によって定義される値は、後の[第12.3節](12-block-finalisation.md#sec:statenoncevalidation)で形式化する。

### 4.4.3. 直列化

<div id="block_preparation_function_for_RLP_serialization_L__B">

</div>

<span id="block_preparation_function_for_RLP_serialization_L__H"></span>関数 $`L_{\mathrm{B}}`$ と $`L_{\mathrm{H}}`$ は、それぞれブロックおよびブロック・ヘッダの準備関数である。RLP変換が必要な場合の構造の型と順序を次のように規定する。

<span id="eq-40"></span><span id="eq-41"></span>

```math
\begin{aligned}
L_{\mathrm{H}}(H) &\equiv \big(H_{\mathrm{p}}, H_{\mathrm{o}}, H_{\mathrm{c}}, H_{\mathrm{r}}, H_{\mathrm{t}}, H_{\mathrm{e}}, H_{\mathrm{b}}, H_{\mathrm{d}},
  H_{\mathrm{i}}, H_{\mathrm{l}}, H_{\mathrm{g}}, H_{\mathrm{s}}, H_{\mathrm{x}}, H_{\mathrm{a}}, H_{\mathrm{n}}, H_{\mathrm{f}}, H_{\mathrm{w}}\big)
  \qquad \text{(40)} \\
L_{\mathrm{B}}(B) &\equiv \big(L_{\mathrm{H}}(B_{\mathrm{H}}), \widetilde{L}_{\mathrm{T}}^{*}(B_{\mathbf{T}}),
  L_{\mathrm{H}}^{*}(B_{\mathbf{U}}), L_{\mathrm{W}}^{*}(B_{\mathbf{W}})\big) \qquad \text{(41)}
\end{aligned}
```

ここで $`\widetilde{L}_{\mathrm{T}}`$ はEIP-2718トランザクションを特別に扱う。

<span id="eq-42"></span>

```math
\widetilde{L}_{\mathrm{T}}(T) = \begin{cases}
L_{\mathrm{T}}(T) & \text{if} \quad T_{\mathrm{x}} = 0 \\
(T_{\mathrm{x}}) \cdot \mathtt{RLP}(L_{\mathrm{T}}(T)) & \text{otherwise}
\end{cases} \qquad \text{(42)}
```

<span id="general_element_wise_sequence_transformation_f_pow_asterisk"></span> $`\widetilde{L}_{\mathrm{T}}^{*}`$ 、 $`L_{\mathrm{H}}^{*}`$ 、 $`L_{\mathrm{W}}^{*}`$ は要素単位の列変換であり、次のとおりである。

<span id="eq-43"></span>

```math
f^{*}\big( (x_0, x_1, ...) \big) \equiv \big( f(x_0), f(x_1), ... \big) \quad \text{（任意の関数 } f \text{ について）} \qquad \text{(43)}
```

構成要素の型を次のように定義する。

<span id="eq-44"></span>

```math
\begin{array}{lclclcl}
H_{\mathrm{p}} \in \mathbb{B}_{32} & \wedge & H_{\mathrm{o}} \in \mathbb{B}_{32} & \wedge & H_{\mathrm{c}} \in \mathbb{B}_{20} & \wedge \\
H_{\mathrm{r}} \in \mathbb{B}_{32} & \wedge & H_{\mathrm{t}} \in \mathbb{B}_{32} & \wedge & H_{\mathrm{e}} \in \mathbb{B}_{32} & \wedge \\
H_{\mathrm{b}} \in \mathbb{B}_{256} & \wedge & H_{\mathrm{d}} \in \mathbb{N} & \wedge & H_{\mathrm{i}} \in \mathbb{N} & \wedge \\
H_{\mathrm{l}} \in \mathbb{N} & \wedge & H_{\mathrm{g}} \in \mathbb{N} & \wedge & H_{\mathrm{s}} \in \mathbb{N}_{256} & \wedge \\
H_{\mathrm{x}} \in \mathbb{B} & \wedge & H_{\mathrm{a}} \in \mathbb{B}_{32} & \wedge & H_{\mathrm{n}} \in \mathbb{B}_{8} & \wedge \\
H_{\mathrm{f}} \in \mathbb{N} & \wedge & H_{\mathrm{w}} \in \mathbb{B}_{32}
\end{array} \qquad \text{(44)}
```

ここで、

<span id="eq-45"></span>

```math
\mathbb{B}_{\mathrm{n}} = \{ B: B \in \mathbb{B} \wedge \lVert B \rVert = n \} \qquad \text{(45)}
```

である。

以上で、形式的なブロック構造を構成する厳密な仕様が得られた。RLP関数 $`\texttt{RLP}`$ （[付録B](../appendices/appendix-b-rlp.md#app:rlp)参照）は、この構造をネットワーク送信またはローカル保存が可能なバイト列へ変換する正準な方法を与える。

### 4.4.4. ブロック・ヘッダの妥当性

$`P(B_{\mathrm{H}})`$ を $`B`$ の親ブロックとして、形式的に次のように定義する。

<span id="eq-46"></span>

```math
P(H) \equiv B': \mathtt{KEC}(\mathtt{RLP}(B'_{\mathrm{H}})) = H_{\mathrm{p}} \qquad \text{(46)}
```

<div id="block_number_H__i">

</div>

ブロック番号は親のブロック番号に1を加えたものである。

<span id="eq-47"></span>

```math
H_{\mathrm{i}} \equiv {{P(H)_{\mathrm{H}}}_{\mathrm{i}}} + 1 \qquad \text{(47)}
```

<span id="H__f"></span>

*London* リリースでは、ブロック属性*gas当たり基本手数料* $`H_{\mathrm{f}}`$[↗](#block_baseFeePerGas_H__f) が導入された（[(Buterin et al. 2019)](../references.md#ref-EIP-1559)によるEIP-1559を参照）。基本手数料とは、ブロック内のトランザクション実行中に消費されるgas 1単位当たりにバーンされるwei量である。その値は、親ブロックが使用したgasと親ブロックの*gas目標値*との差の関数である。

gas当たりの期待基本手数料を $`F(H)`$ として次のように定義する。

<span id="eq-48"></span>

```math
F(H) \equiv \begin{cases}
    1000000000  & \text{if} \quad H_{\mathrm{i}} = F_{\mathrm{London}} \\
    {P(H)_{\mathrm{H}}}_{\mathrm{f}}  & \text{if} \quad {P(H)_{\mathrm{H}}}_{\mathrm{g}} = \tau \\
    {P(H)_{\mathrm{H}}}_{\mathrm{f}} - \nu & \text{if} \quad {P(H)_{\mathrm{H}}}_{\mathrm{g}} < \tau \\
    {P(H)_{\mathrm{H}}}_{\mathrm{f}} + \nu & \text{if} \quad {P(H)_{\mathrm{H}}}_{\mathrm{g}} > \tau
  \end{cases} \qquad \text{(48)}
```

ここで、

<span id="eq-49"></span><span id="eq-50"></span><span id="eq-51"></span><span id="eq-52"></span><span id="eq-53"></span>

```math
\begin{aligned}
\tau &\equiv \lfloor\frac{{P(H)_{\mathrm{H}}}_{\mathrm{l}}}{\rho} \rfloor & \qquad \text{(49)} \\
\rho &\equiv 2 & \qquad \text{(50)} \\
\nu^{*} &\equiv \begin{cases}
      \lfloor \frac{{P(H)_{\mathrm{H}}}_{\mathrm{f}} \times ({\tau - P(H)_{\mathrm{H}}}_{\mathrm{g}})}{\tau} \rfloor &  \text{if} \quad {P(H)_{\mathrm{H}}}_{\mathrm{g}} < \tau \\
      \lfloor \frac{{P(H)_{\mathrm{H}}}_{\mathrm{f}} \times ({P(H)_{\mathrm{H}}}_{\mathrm{g}} - \tau)}{\tau} \rfloor &  \text{if} \quad {P(H)_{\mathrm{H}}}_{\mathrm{g}} > \tau \\
  \end{cases} & \qquad \text{(51)} \\
\nu &\equiv \begin{cases}
    \lfloor \frac{\nu^*}{\xi} \rfloor &  \text{if} \quad {P(H)_{\mathrm{H}}}_{\mathrm{g}} < \tau \\
    max(\lfloor \frac{\nu^*}{\xi} \rfloor, 1) &  \text{if} \quad {P(H)_{\mathrm{H}}}_{\mathrm{g}} > \tau \\
  \end{cases} & \qquad \text{(52)} \\
\xi &\equiv 8 & \qquad \text{(53)}
\end{aligned}
```

*gas目標値* $`\tau`$ は、gas上限 $`H_{\mathrm{l}}`$ を、2に設定された大域定数である*弾力性乗数* $`\rho`$ で割った値として定義される。したがって、各ブロックはgas上限までgasを消費できる一方、平均的にはブロックがgas目標値相当のgasを消費するよう基本手数料が調整される。親ブロックのgas使用量がgas目標値を超える場合、現在のブロックでは基本手数料が引き上げられ、反対に親ブロックのgas使用量がgas目標値を下回る場合は引き下げられる。

基本手数料の増減幅 $`\nu`$ は、親ブロックが消費したgas量と親ブロックのgas目標値との差に比例する。基本手数料への影響は、*基本手数料最大変化分母*と呼ばれる大域定数（形式的には $`\xi`$ ）によって抑制され、その値は8に設定される。値が8であるため、基本手数料が一つのブロックから次のブロックまでに増減できる割合は最大12.5%となる。

<span id="tnref-3"></span>[訳注3](../translation-notes.md#tn-3)

<div id="block_gas_limit_H__l">

</div>

ヘッダ $`H`$ を持つブロックの正準gas上限 $`H_{\mathrm{l}}`$ は、次の関係を満たさなければならない。

<span id="eq-54"></span>

```math
\begin{aligned}
& & H_{\mathrm{l}} < {P(H)_{\mathrm{H}}}_{\mathrm{l}'} + \left\lfloor\frac{{P(H)_{\mathrm{H}}}_{\mathrm{l}'}}{1024}\right\rfloor \quad \wedge & \qquad \text{(54)} \\
& & H_{\mathrm{l}} > {P(H)_{\mathrm{H}}}_{\mathrm{l}'} - \left\lfloor\frac{{P(H)_{\mathrm{H}}}_{\mathrm{l}'}}{1024}\right\rfloor \quad \wedge \\
& & H_{\mathrm{l}} \geqslant 5000
\end{aligned}
```

ここで、

<span id="eq-55"></span>

```math
\begin{aligned}
{P(H)_{\mathrm{H}}}_{\mathrm{l}'} &\equiv \begin{cases}
      {P(H)_{\mathrm{H}}}_{\mathrm{l}} \times \rho &  \text{if} \quad H_{\mathrm{i}} = F_{\mathrm{London}} \\
      {P(H)_{\mathrm{H}}}_{\mathrm{l}} &  \text{if} \quad H_{\mathrm{i}} > F_{\mathrm{London}} \\
  \end{cases} & \qquad \text{(55)}
\end{aligned}
```

gas使用量の不連続を避けるため、現在のブロックのgas上限を検証する際に用いる親ブロックのgas上限値は、*London* フォーク・ブロックにおいて*弾力性乗数* $`\rho`$ を掛けることで修正される。この修正後の値を $`{P(H)_{\mathrm{H}}}_{\mathrm{l}'}`$ と呼ぶ。これにより、*London* 後のブロックのgas目標値を、*London* 前のブロックのgas上限とおおむね同水準に設定できる。

<div id="block_timestamp_H__s">

</div>

$`H_{\mathrm{s}}`$ はブロック $`H`$ のタイムスタンプ（Unix時刻）であり、次の関係を満たさなければならない。

<span id="eq-56"></span>

```math
H_{\mathrm{s}} > {P(H)_{\mathrm{H}}}_{\mathrm{s}} \qquad \text{(56)}
```

*Paris* ハードフォークはEthereumの合意方式をプルーフ・オブ・ワークからプルーフ・オブ・ステークへ変更し、その結果、プルーフ・オブ・ワークに関係する多数のブロック・ヘッダ属性が非推奨となった。これには **nonce** ( $`H_{\mathbf{n}}`$ )、**ommersHash** ( $`H_{\mathbf{o}}`$ )、**difficulty** ( $`H_{\mathbf{d}}`$ )、**mixHash** ( $`H_{\mathbf{m}}`$ ) が含まれる。

**mixHash** は新たなフィールド **prevRandao** ( $`H_{\mathbf{a}}`$ ) に置き換えられた。プルーフ・オブ・ワークに関係するほかのヘッダ・フィールドは、次の定数に置き換えられた。

<span id="eq-57"></span><span id="eq-58"></span><span id="eq-59"></span>

```math
\begin{aligned}
H_{\mathrm{o}} & \equiv & \texttt{KEC}(\texttt{RLP}(())) & \qquad \text{(57)} \\
H_{\mathrm{d}} & \equiv  & 0 & \qquad \text{(58)} \\
H_{\mathrm{n}}  & \equiv & \texttt{0x0000000000000000} & \qquad \text{(59)}
\end{aligned}
```

**prevRandao** の値はBeacon Chainの情報を用いて決定しなければならない。Beacon Chain上で *RANDAO* 値を生成する詳細は本稿の範囲外であるが、直前のブロックについて期待される *RANDAO* 値を $`\mathtt{PREVRANDAO}()`$ と表す。

<div id="block_header_validity_function">

</div>

以上により、ブロック・ヘッダ妥当性関数 $`V(H)`$ を次のように定義できる。

<span id="eq-60"></span>

```math
\begin{aligned}
V(H) & \equiv & H_{\mathrm{g}} \le H_{\mathrm{l}}  \quad \wedge & \qquad \text{(60)} \\
& & H_{\mathrm{l}} < {P(H)_{\mathrm{H}}}_{\mathrm{l}'} + \left\lfloor\frac{{P(H)_{\mathrm{H}}}_{\mathrm{l}'}}{1024}\right\rfloor  \quad \wedge \\
& & H_{\mathrm{l}} > {P(H)_{\mathrm{H}}}_{\mathrm{l}'} - \left\lfloor\frac{{P(H)_{\mathrm{H}}}_{\mathrm{l}'}}{1024}\right\rfloor  \quad \wedge \\
& & H_{\mathrm{l}} \geqslant 5000  \quad \wedge \\
& & H_{\mathrm{s}} > {P(H)_{\mathrm{H}}}_{\mathrm{s}} \quad \wedge \\
& & H_{\mathrm{i}} = {P(H)_{\mathrm{H}}}_{\mathrm{i}} +1 \quad \wedge \\
& & \lVert H_{\mathrm{x}} \rVert \le 32 \quad \wedge \\
& & H_{\mathrm{f}} = F(H) \wedge \\
& & H_{\mathrm{o}} = \texttt{KEC}(\texttt{RLP}(())) \quad \wedge \\
& & H_{\mathrm{d}} = 0 \quad \wedge \\
& & H_{\mathrm{n}} = \texttt{0x0000000000000000} \quad \wedge \\
& & H_{\mathrm{a}} = \mathtt{PREVRANDAO}()
\end{aligned}
```

さらに、**extraData** は最大32バイトでなければならない。

[^3]: 特に、このような「道具」は最終的に、人間による開始から因果的に大きく切り離されるか、人間が因果的に極めて中立となり、自律的主体とみなすのが正当な段階へ達する可能性がある。たとえばコントラクトが、自身の実行を開始するトランザクションを送る人間へ報奨金を提示する場合があり得る。

[^4]: *優先手数料*については[第5節](05-gas-and-payment.md#ch:payment)および[第6節](06-transaction-execution.md#ch:transactions)で詳しく論じる。

[^5]: 型0および型1トランザクションは、 <var>T</var><sub>m</sub> と <var>T</var><sub>f</sub> を <var>T</var><sub>p</sub> の値に設定した型2トランザクションと同じgas価格の挙動を示す。

[^6]: *ommer* は「親のきょうだい」を意味するジェンダー中立な用語である。<https://nonbinary.miraheze.org/wiki/Gender_neutral_language_in_English#Aunt/Uncle>を参照されたい。

[^7]: RANDAOはEthereum合意レイヤーのバリデータが生成する疑似乱数値である。RANDAOの詳細は合意レイヤー仕様（<https://github.com/ethereum/consensus-specs>）を参照されたい。

[^8]: 2048 = 2<sup>11</sup> （11ビット）であり、下位11ビットはオペランドを2048で割った剰余である。この場合のオペランドは「バイト列のKeccak-256ハッシュの先頭三つの各2バイト対」である。
