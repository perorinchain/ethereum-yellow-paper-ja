[分割版目次](../README.md) | [前へ](appendix-a-terminology.md) | [次へ](appendix-c-hex-prefix.md) | [単一ページ版](../../ethereum_yellow_paper_ja.md)

<span id="app:rlp"></span>

# 付録B. 再帰的長さ接頭辞

<div id="rlp">

</div>

これは、任意構造のバイナリ・データ（バイト配列）を符号化する直列化方式である。

可能な構造の集合 $`\mathbb{T}`$ を次のように定義する。

<span id="eq-190"></span><span id="eq-191"></span><span id="eq-192"></span>

```math
\begin{aligned}
\mathbb{T} & \equiv & \mathbb{L} \uplus \mathbb{B} & \qquad \text{(190)} \\
\mathbb{L} & \equiv & \{ \mathbf{t}: \mathbf{t} = ( \mathbf{t}[0], \mathbf{t}[1], ... ) \; \wedge \; \forall n < \lVert \mathbf{t} \rVert : \mathbf{t}[n] \in \mathbb{T} \} & \qquad \text{(191)} \\
\mathbb{B} & \equiv & \{ \mathbf{b}: \mathbf{b} = ( \mathbf{b}[0], \mathbf{b}[1], ... ) \; \wedge \; \forall n < \lVert \mathbf{b} \rVert : \mathbf{b}[n] \in \mathbb{O} \} & \qquad \text{(192)}
\end{aligned}
```

ここで $`\mathbb{O}`$ は（8ビット）バイトの集合である。したがって $`\mathbb{B}`$ はすべてのバイト列（バイト配列とも呼ばれ、木として考えれば葉）の集合、 $`\mathbb{L}`$ は単一の葉ではないすべての木状（部分）構造（木として考えれば分岐ノード）の集合、 $`\mathbb{T}`$ はすべてのバイト配列およびそのような構造列の集合である。非交和 $`\uplus`$ が必要なのは、空バイト配列 $`()\in\mathbb{B}`$ と空リスト $`()\in\mathbb{L}`$ を区別するためだけである。両者は後述の定義どおり異なる方法で符号化される。慣例に従い、記法を濫用して非交和の添字を省略し、文脈から推論できるものとする。

RLP関数 $`\mathtt{RLP}`$ を二つの補助関数によって定義する。一つ目は値がバイト配列の場合を、二つ目は値がさらに値を含む列である場合を扱う。

<span id="eq-193"></span>

```math
\mathtt{RLP}(\mathbf{x}) \equiv \begin{cases} R_{\mathrm{b}}(\mathbf{x}) & \text{if} \quad \mathbf{x} \in \mathbb{B} \\ R_{\mathrm{l}}(\mathbf{x}) & \text{otherwise} \end{cases} \qquad \text{(193)}
```

<div id="RLP_serialisation_of_a_byte_array_R__b_word_def">

</div>

直列化する値がバイト配列の場合、RLP 直列化は次の3形式のいずれかをとる。

- バイト配列が単一のバイトだけを含み、そのバイトが128未満なら、入力は出力と厳密に等しい。

- バイト配列が56バイト未満なら、出力は入力の前に、バイト配列長に128を加えた値に等しいバイトを付けたものとなる。

- それ以外では、入力が $`2^{64}`$ バイト未満である場合、入力の前に、ビッグエンディアン整数として解釈すると入力バイト配列長に等しくなる最小長バイト配列を付け、さらにその前に、この長さ値を忠実に符号化するために必要なバイト数に183を加えた値を付けたものが出力となる。

$`2^{64}`$ バイト以上のバイト配列は符号化できない。この制限により、バイト配列の符号化の先頭バイトは常に192未満となり、 $`\mathbb{L}`$ の列の符号化と容易に区別できる。

<div id="RLP_serialisation_of_a_byte_array_R__b_math_def">

</div>

形式的には、 $`R_{\mathrm{b}}`$ を次のように定義する。

<span id="eq-194"></span><span id="eq-195"></span><span id="eq-196"></span><span id="eq:BE"></span>

```math
\begin{aligned}
R_{\mathrm{b}}(\mathbf{x}) & \equiv & \begin{cases}
\mathbf{x} & \text{if} \quad \lVert \mathbf{x} \rVert = 1 \wedge \mathbf{x}[0] < 128 \\
(128 + \lVert \mathbf{x} \rVert) \cdot \mathbf{x} & \text{else if} \quad \lVert \mathbf{x} \rVert < 56 \\
\big(183 + \big\lVert \mathtt{BE}(\lVert \mathbf{x} \rVert) \big\rVert \big) \cdot \mathtt{BE}(\lVert \mathbf{x} \rVert) \cdot \mathbf{x} & \text{else if} \quad \lVert \mathbf{x} \rVert < 2^{64} \\
\varnothing & \text{otherwise}
\end{cases} & \qquad \text{(194)} \\
\mathtt{BE}(x) & \equiv & (b_0, b_1, ...): b_0 \neq 0 \wedge x = \sum_{n = 0}^{\lVert \mathbf{b} \rVert - 1} b_n \cdot 256^{\lVert \mathbf{b} \rVert - 1 - n} & \qquad \text{(195)} \\
(x_1, ..., x_n) \cdot (y_1, ..., y_m) & = & (x_1, ..., x_n, y_1, ..., y_m) & \qquad \text{(196)}
\end{aligned}
```

したがって $`\mathtt{BE}`$ は、非負整数値を最小長のビッグエンディアン・バイト配列へ展開する関数であり、ドット演算子は列の連結を行う。

<div id="RLP_serialisation_of_a_sequence_of_other_items_R__l_word_def">

</div>

一方、直列化する値がほかの項目の列である場合、RLP 直列化は次の2形式のいずれかをとる。

- 各項目の直列化を連結した長さが56バイト未満なら、出力はその連結結果の前に、そのバイト配列長に192を加えた値に等しいバイトを付けたものとなる。

- それ以外では、連結した直列化が $`2^{64}`$ バイト未満である場合、その前に、ビッグエンディアン整数として解釈すると連結済み直列化バイト配列長に等しくなる最小長バイト配列を付け、さらにその前に、この長さ値を忠実に符号化するために必要なバイト数に247を加えた値を付けたものが出力となる。

連結した直列化項目が $`2^{64}`$ バイト以上となる列は符号化できない。この制限により、符号化の先頭バイトは255を超えない（超えればバイトではなくなる）。

<div id="RLP_serialisation_of_a_sequence_of_other_items_R__l_math_def">

</div>

以上から、最後に $`R_{\mathrm{l}}`$ を形式的に定義する。

<span id="eq-197"></span><span id="eq-198"></span>

```math
\begin{aligned}
R_{\mathrm{l}}(\mathbf{x}) & \equiv & \begin{cases}
(192 + \lVert s(\mathbf{x}) \rVert) \cdot s(\mathbf{x}) & \text{if} \quad s(\mathbf{x}) \neq \varnothing \wedge \lVert s(\mathbf{x}) \rVert < 56 \\
\big(247 + \big\lVert \mathtt{BE}(\lVert s(\mathbf{x}) \rVert) \big\rVert \big) \cdot \mathtt{BE}(\lVert s(\mathbf{x}) \rVert) \cdot s(\mathbf{x}) & \text{else if} \quad s(\mathbf{x}) \neq \varnothing \wedge \lVert s(\mathbf{x}) \rVert < 2^{64} \\
\varnothing & \text{otherwise}
\end{cases} & \qquad \text{(197)} \\
s(\mathbf{x}) & \equiv & \begin{cases}
\mathtt{RLP}(\mathbf{x}[0]) \cdot \mathtt{RLP}(\mathbf{x}[1]) \cdot ... & \text{if} \quad \forall i: \mathtt{RLP}(\mathbf{x}[i]) \neq \varnothing \\
\varnothing & \text{otherwise}
\end{cases} & \qquad \text{(198)}
\end{aligned}
```

非負整数（ $`\mathbb{N}`$ 、または任意の $`x`$ に対する $`\mathbb{N}_x`$ ）としてのみ定義されるスカラーをRLPで符号化する場合、ビッグエンディアンとして解釈するとそのスカラーになる最短のバイト配列として符号化しなければならない。したがって、非負整数 $`i`$ のRLPを次のように定義する。

<span id="eq-199"></span>

```math
\mathtt{RLP}(i : i \in \mathbb{N}) \equiv \mathtt{RLP}(\mathtt{BE}(i)) \qquad \text{(199)}
```

RLPデータの解釈時に、スカラーとして復号されるべき断片のバイト列に先頭ゼロが見つかった場合、クライアントはそれを非正準とみなし、ほかの無効なRLPデータと同様に完全に棄却しなければならない。

符号付き値または浮動小数点値について、特定の正準符号化形式はない。
