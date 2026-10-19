[分割版目次](../README.md) | [前へ](08-message-call.md) | [次へ](10-proof-of-stake-transition.md) | [単一ページ版](../../ethereum_yellow_paper_ja.md)

<span id="ch:model"></span>

# 9. 実行モデル

実行モデルは、バイトコード命令列と環境データの小さなタプルが与えられたとき、システム状態をどのように変更するかを規定する。これは Ethereum 仮想マシン（EVM）として知られる仮想状態機械の形式モデルによって規定される。EVM は*準*チューリング完全な機械である。「準」という限定は、実行できる計算の総量を制限する *gas* というパラメータにより、計算が本質的に有界であることに由来する。

## 9.1. 基礎

EVM は単純なスタック・ベースのアーキテクチャである。マシンのワード・サイズ（したがってスタック項目のサイズ）は256ビットである。これは Keccak-256 ハッシュ方式と楕円曲線計算を容易にするために選ばれた。メモリ・モデルは単純なワード・アドレス指定バイト配列である。スタックの最大サイズは $`1024`$ である。マシンには独立したストレージ・モデルもある。概念上はメモリに似るが、バイト配列ではなくワード・アドレス指定可能なワード配列である。揮発性のメモリと異なり、ストレージは不揮発性で、システム状態の一部として維持される。ストレージとメモリのすべての位置は、初期状態でゼロと明確に定義される。

<span id="tnref-4"></span>[訳注4](../translation-notes.md#tn-4)

マシンは標準的なフォン・ノイマン・アーキテクチャには従わない。プログラム・コードを一般にアクセス可能なメモリまたはストレージへ格納せず、特殊命令を介してのみ相互作用できる仮想 ROM に別途格納する。

マシンは、スタック・アンダーフローや無効な命令など、いくつかの理由で例外実行となり得る。gas 不足例外と同様、状態変更は維持されない。マシンは直ちに停止し、問題を実行主体（トランザクション処理器、または再帰的には実行を生成した環境）へ報告し、実行主体が別途処理する。

## 9.2. 手数料の概要

gas建ての手数料は三つの異なる状況で課され、いずれも演算実行の前提条件となる。第一かつ最も一般的なのは、演算の計算に固有の手数料である（[付録G](../appendices/appendix-g-fee-schedule.md#app:fees)参照）。第二に、下位のメッセージ呼び出しまたはコントラクト作成への支払いを構成するためgasが差し引かれることがある。これはCREATE、CREATE2、CALL、CALLCODEへの支払いの一部となる。最後に、メモリ使用量の増加によりgasが支払われることがある。

アカウントの実行全体にわたり、支払うべきメモリ使用手数料の総額は、読み書きを問わずすべてのメモリ・インデックスを範囲内に含めるために必要な32バイトの最小倍数に比例する。これは必要時に支払われるため、以前に索引付けしたいかなるメモリよりも少なくとも32バイト先の領域を参照すれば、必ず追加のメモリ使用手数料が生じる。この手数料により、アドレスが32ビットの境界を超える可能性は極めて低い。それでも実装はこの事態を処理できなければならない。

ストレージ手数料の挙動はやや複雑である。ストレージ使用量（全ノード上の状態データベースの増大に直結する）の最小化を促すため、ストレージ項目を消去する演算では実行手数料が免除されるだけでなく、条件付きの還付が与えられる。実際には、ストレージ位置を最初に使用するコストが通常使用より大幅に高いため、この還付は事実上前払いされている。

EVMのgasコストの厳密な定義は[付録H](../appendices/appendix-h-virtual-machine.md#app:vm)を参照されたい。

<span id="exec_env"></span>

## 9.3. 実行環境

実行環境では、システム状態 $`\boldsymbol{\sigma}`$ 、計算に残されたgas $`g`$ 、累積サブ状態 $`A`$ に加えて、実行主体が提供しなければならない重要な情報がいくつか用いられる。これらはタプル $`I`$ に含まれる。

- $`I_{\mathrm{a}}`$ ：実行中のコードを所有するアカウントのアドレス。

- $`I_{\mathrm{o}}`$ ：この実行の起点となったトランザクションの送信者アドレス。

- $`I_{\mathrm{p}}`$ ：この実行の起点となったトランザクションの署名者が支払うgas価格。[第6節](06-transaction-execution.md#ch:transactions)の実効gas価格 $`p`$[↗](06-transaction-execution.md#effective_gas_price_p) として定義される。

- $`I_{\mathbf{d}}`$ ：この実行への入力データであるバイト配列。実行主体がトランザクションなら、トランザクション・データとなる。

- $`I_{\mathrm{s}}`$ ：コードを実行させたアカウントのアドレス。実行主体がトランザクションなら、トランザクション送信者となる。

- $`I_{\mathrm{v}}`$ ：実行と同じ手続きの一部としてこのアカウントへ渡されるWei単位の値。実行主体がトランザクションなら、トランザクション値となる。

- $`I_{\mathbf{b}}`$ ：実行するマシン・コードのバイト配列。

- $`I_{\mathrm{H}}`$ ：現在のブロックのブロック・ヘッダ。

- $`I_{\mathrm{e}}`$ ：現在のメッセージ呼び出しまたはコントラクト作成の深さ（現在実行中のCALLまたはCREATE(2)の数）。

- $`I_{\mathrm{w}}`$ ：状態変更の許可。

実行モデルは関数 $`\Xi`$ を定義する。この関数は、これらの定義が与えられたとき、結果状態 $`\boldsymbol{\sigma}'`$ 、残存gas $`g'`$ 、結果の累積サブ状態 $`A'`$ 、結果出力 $`\mathbf{o}`$ を計算できる。ここでは次のように定義する。

<span id="eq-143"></span>

```math
(\boldsymbol{\sigma}', g', A', \mathbf{o}) \equiv \Xi(\boldsymbol{\sigma}, g, A, I) \qquad \text{(143)}
```

なお、累積サブ状態 $`A`$ は[第6.1節](06-transaction-execution.md#ch:substate)で定義したものである。

## 9.4. 実行の概要

ここで $`\Xi`$ 関数を定義しなければならない。実用的な実装の多くでは、完全なシステム状態 $`\boldsymbol{\sigma}`$ とマシン状態 $`\boldsymbol{\mu}`$ の対を反復的に進行させるものとしてモデル化される。形式的には、関数 $`X`$ を用いて再帰的に定義する。これは、状態機械の1サイクルの結果を定義する反復関数 $`O`$ と、現在状態がマシンの[例外停止](#zhalt)状態かどうかを判定する関数 $`Z`$[↗](#zhalt)、および現在状態がマシンの[正常停止](#hhalt)状態である場合、かつその場合に限り命令の出力データを指定する関数 $`H`$[↗](#hhalt) を用いる。

<div id="empty_sequence_vs_empty_set">

</div>

$`()`$ と表す空列は、 $`\varnothing`$ と表す空集合とは等しくない。これは $`H`$ の出力を解釈する際に重要である。実行を継続すべきとき $`H`$ は $`\varnothing`$ と評価され、停止すべきときは（空である可能性もある）列と評価される。

<span id="eq-144"></span><span id="eq-145"></span><span id="eq-146"></span><span id="eq-147"></span><span id="eq-148"></span><span id="eq-149"></span><span id="eq-150"></span><span id="eq-151"></span>

```math
\begin{aligned}
\Xi(\boldsymbol{\sigma}, g, A, I) & \equiv & (\boldsymbol{\sigma}'\!, \boldsymbol{\mu}'_{\mathrm{g}}, A', \mathbf{o}) & \qquad \text{(144)} \\
(\boldsymbol{\sigma}', \boldsymbol{\mu}'\!, A', ..., \mathbf{o}) & \equiv & X\big((\boldsymbol{\sigma}, \boldsymbol{\mu}, A, I)\big) & \qquad \text{(145)} \\
\boldsymbol{\mu}_{\mathrm{g}} & \equiv & g & \qquad \text{(146)} \\
\boldsymbol{\mu}_{\mathrm{pc}} & \equiv & 0 & \qquad \text{(147)} \\
\boldsymbol{\mu}_{\mathbf{m}} & \equiv & (0, 0, ...) & \qquad \text{(148)} \\
\boldsymbol{\mu}_{\mathrm{i}} & \equiv & 0 & \qquad \text{(149)} \\
\boldsymbol{\mu}_{\mathbf{s}} & \equiv & () & \qquad \text{(150)} \\
\boldsymbol{\mu}_{\mathbf{o}} & \equiv & () & \qquad \text{(151)}
\end{aligned}
```

<span id="eq-152"></span><span id="eq:X-def"></span>

```math
X\big( (\boldsymbol{\sigma}, \boldsymbol{\mu}, A, I) \big) \equiv \begin{cases}
\big(\varnothing, \boldsymbol{\mu}, A, I, \varnothing\big) & \text{if} \quad Z(\boldsymbol{\sigma}, \boldsymbol{\mu}, A, I) \\
\big(\varnothing, \boldsymbol{\mu}', A, I, \mathbf{o}\big) & \text{if} \quad w = \text{REVERT} \\
O(\boldsymbol{\sigma}, \boldsymbol{\mu}, A, I) \cdot \mathbf{o} & \text{if} \quad \mathbf{o} \neq \varnothing \\
X\big(O(\boldsymbol{\sigma}, \boldsymbol{\mu}, A, I)\big) & \text{otherwise} \\
\end{cases} \qquad \text{(152)}
```

ここで、

<span id="eq-153"></span><span id="eq-154"></span><span id="eq-155"></span><span id="eq-156"></span>

```math
\begin{aligned}
\mathbf{o} & \equiv & H(\boldsymbol{\mu}, I) & \qquad \text{(153)} \\
(a, b, c, d) \cdot e & \equiv & (a, b, c, d, e) & \qquad \text{(154)} \\
\boldsymbol{\mu}' & \equiv & \boldsymbol{\mu}\ \text{except:} & \qquad \text{(155)} \\
\boldsymbol{\mu}'_{\mathrm{g}} & \equiv & \boldsymbol{\mu}_{\mathrm{g}} - C(\boldsymbol{\sigma}, \boldsymbol{\mu}, A, I) & \qquad \text{(156)}
\end{aligned}
```

$`\Xi`$ を評価するときは、第4要素 $`I'`$ を捨て、結果のマシン状態 $`\boldsymbol{\mu}'`$ から残存gas $`\boldsymbol{\mu}'_{\mathrm{g}}`$ を取り出す点に注意されたい。

このように、$`Z`$[↗](#zhalt) が真となって現在状態が例外的であり、マシンを停止してすべての変更を破棄すべきことを示すか、$`H`$[↗](#hhalt) が空集合ではなく列となってマシンが制御された停止に達したことを示すまで、 $`X`$ を循環させる（ここでは再帰的だが、実装では通常、単純な反復ループを用いることが期待される）。

### 9.4.1. マシン状態

マシン状態 $`\boldsymbol{\mu}`$ はタプル $`(g, pc, \mathbf{m}, i, \mathbf{s}, \mathbf{o})`$ として定義される。各要素は、利用可能なgas、プログラム・カウンタ $`pc \in \mathbb{N}_{256}`$ 、メモリ内容、メモリ内の有効ワード数（位置0から連続して数える）、スタック内容、リターン・データ・バッファである。メモリ内容 $`\boldsymbol{\mu}_{\mathbf{m}}`$ は、大きさ $`2^{256}`$ のゼロ列である。

読みやすさのため、スモールキャップで記した命令ニーモニック（例：ADD）は、その数値表現として解釈されたい。命令の完全な表と詳細は[付録H](../appendices/appendix-h-virtual-machine.md#app:vm)に示す。

$`Z`$ 、 $`H`$ 、 $`O`$ を定義するため、 $`w`$ を現在実行される演算として定義する。

<span id="eq-157"></span><span id="eq:currentoperation"></span>

```math
w \equiv \begin{cases} I_{\mathbf{b}}[\boldsymbol{\mu}_{\mathrm{pc}}] & \text{if} \quad \boldsymbol{\mu}_{\mathrm{pc}} < \lVert I_{\mathbf{b}} \rVert \\
\text{STOP} & \text{otherwise}
\end{cases} \qquad \text{(157)}
```

さらに、削除および追加されるスタック項目数を指定する固定量 $`\mathbf{\delta}`$ と $`\mathbf{\alpha}`$ を仮定する。いずれも命令によって添字付けでき、命令コスト関数 $`C`$ は与えられた命令を実行する完全なコストをgas単位で評価する。

<span id="zhalt"></span>

### 9.4.2. 例外停止

<div id="Exceptional_Halting_function_Z">

</div>

例外停止関数 $`Z`$ を次のように定義する。

<span id="eq-158"></span>

```math
Z(\boldsymbol{\sigma}, \boldsymbol{\mu}, A, I) \equiv
\begin{array}{l}
\boldsymbol{\mu}_g < C(\boldsymbol{\sigma}, \boldsymbol{\mu}, A, I) \quad \vee \\
\mathbf{\delta}_w = \varnothing \quad \vee \\
\lVert\boldsymbol{\mu}_\mathbf{s}\rVert < \mathbf{\delta}_w \quad \vee \\
( w = \text{JUMP} \; \wedge \; \boldsymbol{\mu}_\mathbf{s}[0] \notin D(I_\mathbf{b}) ) \quad \vee \\
( w = \text{JUMPI} \; \wedge \; \boldsymbol{\mu}_\mathbf{s}[1] \neq 0 \; \wedge \\
\quad \boldsymbol{\mu}_\mathbf{s}[0] \notin D(I_\mathbf{b}) ) \quad \vee \\
( w = \text{RETURNDATACOPY} \; \wedge \\ \quad \boldsymbol{\mu}_{\mathbf{s}}[1] + \boldsymbol{\mu}_{\mathbf{s}}[2] > \lVert\boldsymbol{\mu}_{\mathbf{o}}\rVert) \quad \vee \\
\lVert\boldsymbol{\mu}_\mathbf{s}\rVert - \mathbf{\delta}_w + \mathbf{\alpha}_w > 1024 \quad \vee \\
( \neg I_{\mathrm{w}} \; \wedge \; W(w, \boldsymbol{\mu}) ) \quad \vee \\
( w = \text{SSTORE} \; \wedge \; \boldsymbol{\mu}_g \leqslant G_{\mathrm{callstipend}} )
\end{array} \qquad \text{(158)}
```

ここで、

<span id="eq-159"></span>

```math
W(w, \boldsymbol{\mu}) \equiv
\begin{array}{l}
w \in \{\text{CREATE}, \text{CREATE2}, \text{SSTORE},\\ \text{SELFDESTRUCT}\} \ \vee \\
\text{LOG0} \le w \; \wedge \; w \le \text{LOG4} \quad \vee \\
w = \text{CALL} \; \wedge \; \boldsymbol{\mu}_{\mathbf{s}}[2] \neq 0
\end{array} \qquad \text{(159)}
```

これは、gasが不足する場合、命令が無効である（したがってその $`\delta`$ 添字が未定義である）場合、スタック項目が不足する場合、JUMP/JUMPIの宛先が無効である場合、新しいスタック・サイズが1024を超える場合、または静的呼び出し中に状態変更を試みる場合に、実行が例外停止状態となることを述べている。注意深い読者は、これが、いかなる命令もその実行途中で例外停止を引き起こすことはない、ということを含意すると分かるだろう。また、[SSTORE](../appendices/appendix-h-virtual-machine.md#SSTORE)命令を実行する直前の残存gasが呼び出し給付量 $`G_{\mathrm{callstipend}}`$ 以下である場合も実行は例外停止状態となる。詳細は[(Tang 2019)](../references.md#ref-EIP-2200)によるEIP-2200を参照されたい。

### 9.4.3. ジャンプ先の妥当性

先に、実行中のコードが与えられたとき妥当なジャンプ先の集合を決定する関数として $`D`$ を用いた。これを、コード内でJUMPDEST命令が占めるすべての位置として定義する。

そのような位置はすべて、PUSH演算のデータ部分ではなく妥当な命令境界上になければならず、コード末尾に暗黙に定義される[STOP](../appendices/appendix-h-virtual-machine.md#stop)演算ではなく、コードの明示的に定義された部分内に現れなければならない。

形式的には、

<span id="eq-160"></span>

```math
D(\mathbf{c}) \equiv D_{\mathrm{J}}(\mathbf{c}, 0) \qquad \text{(160)}
```

ここで、

<span id="eq-161"></span>

```math
D_{\mathrm{J}}(\mathbf{c}, i) \equiv \begin{cases}
\{\} & \text{if} \quad i \geqslant \lVert \mathbf{c} \rVert  \\
\{ i \} \cup D_{\mathrm{J}}(\mathbf{c}, N(i, \mathbf{c}[i])) & \\
\quad\quad\text{if} \quad \mathbf{c}[i] = \text{JUMPDEST} \\
D_{\mathrm{J}}(\mathbf{c}, N(i, \mathbf{c}[i])) & \text{otherwise} \\
\end{cases} \qquad \text{(161)}
```

ここで $`N`$ は、PUSH命令のデータがあればそれを飛ばした、コード内の次の妥当な命令位置である。

<span id="eq-162"></span>

```math
N(i, w) \equiv \begin{cases}
i + w - \text{PUSH1} + 2 & \\
\quad\quad\text{if} \quad w \in [\text{PUSH1}, \text{PUSH32}] \\
i + 1 & \text{otherwise} \end{cases} \qquad \text{(162)}
```

<span id="hhalt"></span>

### 9.4.4. 正常停止

<div id="normal_halting_function_H">

</div>

正常停止関数 $`H`$ を次のように定義する。

<span id="eq-163"></span>

```math
H(\boldsymbol{\mu}, I) \equiv \begin{cases}
H_{\text{RETURN}}(\boldsymbol{\mu}) \ \text{if} \quad w \in \{\text{RETURN}, \text{REVERT}\} &\\
() \quad\quad\ \text{if} \quad w \in \{ \text{STOP}, \text{SELFDESTRUCT} \} &\\
\varnothing \quad\quad\ \text{otherwise}&
\end{cases} \qquad \text{(163)}
```

データを返す停止演算 [RETURN](../appendices/appendix-h-virtual-machine.md#RETURN) と [REVERT](../appendices/appendix-h-virtual-machine.md#REVERT) には、特別な関数 $`H_{\text{RETURN}}`$ がある。[ここ](#empty_sequence_vs_empty_set)で論じた空列と空集合の違いにも注意されたい。

## 9.5. 実行サイクル

スタック項目は列の左端、すなわち低いインデックス側で追加または削除される。ほかのすべての項目は変化しない。

<span id="eq-164"></span><span id="eq-165"></span><span id="eq-166"></span><span id="eq-167"></span>

```math
\begin{aligned}
O\big((\boldsymbol{\sigma}, \boldsymbol{\mu}, A, I)\big) & \equiv & (\boldsymbol{\sigma}', \boldsymbol{\mu}', A', I) & \qquad \text{(164)} \\
\Delta & \equiv & \mathbf{\alpha}_{w} - \mathbf{\delta}_{w} & \qquad \text{(165)} \\
\lVert\boldsymbol{\mu}'_{\mathbf{s}}\rVert & \equiv & \lVert\boldsymbol{\mu}_{\mathbf{s}}\rVert + \Delta & \qquad \text{(166)} \\
\quad \forall x \in [\mathbf{\alpha}_{w}, \lVert\boldsymbol{\mu}'_{\mathbf{s}}\rVert): \boldsymbol{\mu}'_{\mathbf{s}}[x] & \equiv & \boldsymbol{\mu}_{\mathbf{s}}[x-\Delta] & \qquad \text{(167)}
\end{aligned}
```

gasは命令のgasコストだけ減少し、ほとんどの命令ではプログラム・カウンタが各サイクルで増加する。三つの例外については、二つの命令のいずれかで添字付けされ、対応する値へ評価される関数 $`J`$ を仮定する。

<span id="eq-168"></span><span id="eq-169"></span><span id="eq:mu_pc"></span>

```math
\begin{aligned}
\quad \boldsymbol{\mu}'_{\mathrm{g}} & \equiv & \boldsymbol{\mu}_{\mathrm{g}} - C(\boldsymbol{\sigma}, \boldsymbol{\mu}, A, I) & \qquad \text{(168)} \\
\quad \boldsymbol{\mu}'_{\mathrm{pc}} & \equiv & \begin{cases}
J_{\text{JUMP}}(\boldsymbol{\mu}) & \text{if} \quad w = \text{JUMP} \\
J_{\text{JUMPI}}(\boldsymbol{\mu}) & \text{if} \quad w = \text{JUMPI} \\
N(\boldsymbol{\mu}_{\mathrm{pc}}, w) & \text{otherwise}
\end{cases} & \qquad \text{(169)}
\end{aligned}
```

一般に、メモリ、累積サブ状態、システム状態は変化しないと仮定する。

<span id="eq-170"></span><span id="eq-171"></span><span id="eq-172"></span><span id="eq-173"></span>

```math
\begin{aligned}
\boldsymbol{\mu}'_{\mathbf{m}} & \equiv & \boldsymbol{\mu}_{\mathbf{m}} & \qquad \text{(170)} \\
\boldsymbol{\mu}'_{\mathrm{i}} & \equiv & \boldsymbol{\mu}_{\mathrm{i}} & \qquad \text{(171)} \\
A' & \equiv & A & \qquad \text{(172)} \\
\boldsymbol{\sigma}' & \equiv & \boldsymbol{\sigma} & \qquad \text{(173)}
\end{aligned}
```

ただし命令は通常、これらの値の一つ以上の構成要素を変更する。命令ごとに変更される構成要素は、 $`\alpha`$ と $`\delta`$ の値およびgas要件の形式的記述とともに[付録H](../appendices/appendix-h-virtual-machine.md#app:vm)に記載する。
