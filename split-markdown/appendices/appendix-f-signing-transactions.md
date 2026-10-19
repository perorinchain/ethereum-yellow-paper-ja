[分割版目次](../README.md) | [前へ](appendix-e-precompiled-contracts.md) | [次へ](appendix-g-fee-schedule.md) | [単一ページ版](../../ethereum_yellow_paper_ja.md)

<span id="app:signing"></span>

# 付録F. トランザクションへの署名

トランザクションは、公開鍵を復元可能なECDSA署名を用いて署名される。この方式は [(Courtois, Grajek, and Naik 2014)](../references.md#ref-Courtois2014) が記述するSECP-256k1曲線を使用し、[(Gura et al. 2004)](../references.md#ref-gura2004comparing) の全15ページ中9ページ、第3段落に記述された方法と同様に実装される。

送信者は妥当な秘密鍵 $`p_{\mathrm{r}}`$ を持つと仮定する。これは範囲 $`[1, \mathtt{secp256k1n} - 1]`$ から無作為に選ばれた正整数であり、ビッグエンディアン形式の長さ32のバイト配列として表される。

関数 $`\mathtt{ECDSAPUBKEY}`$ 、 $`\mathtt{ECDSASIGN}`$ 、 $`\mathtt{ECDSARECOVER}`$ が存在すると仮定する。これらは、たとえば[(Johnson, Menezes, and Vanstone 2001)](../references.md#ref-ECDSAcerticom)などの文献で形式的に定義されている。

<span id="eq-309"></span><span id="eq-310"></span><span id="eq-311"></span>

```math
\begin{aligned}
\mathtt{ECDSAPUBKEY}(p_{\mathrm{r}} \in \mathbb{B}_{32}) & \equiv & p_{\mathrm{u}} \in \mathbb{B}_{64} & \qquad \text{(309)} \\
\mathtt{ECDSASIGN}(e \in \mathbb{B}_{32}, p_{\mathrm{r}} \in \mathbb{B}_{32}) & \equiv & (v \in \mathbb{B}_{1}, r \in \mathbb{B}_{32}, s \in \mathbb{B}_{32}) & \qquad \text{(310)} \\
\mathtt{ECDSARECOVER}(e \in \mathbb{B}_{32}, v \in \mathbb{B}_{1}, r \in \mathbb{B}_{32}, s \in \mathbb{B}_{32}) & \equiv & p_{\mathrm{u}} \in \mathbb{B}_{64} & \qquad \text{(311)}
\end{aligned}
```

ここで $`p_{\mathrm{u}}`$ は公開鍵であり、それぞれ $`2^{256}`$ 未満である二つの正整数を連結して構成した64バイトのバイト配列と仮定する。 $`p_{\mathrm{r}}`$ は秘密鍵であり、32バイトのバイト配列（または前述の範囲内の単一の正整数）である。また $`e`$ はトランザクションのハッシュ $`h(T)`$[↗](#h_of_T) である。<span id="v"></span> $`v`$ は「復元識別子（recovery identifier）」と仮定する。復元識別子は、 $`r`$ がx座標となる曲線上の点について、その座標の偶奇性と有限性を指定する1バイト値である。この値の範囲は $`[0, 3]`$ だが、無限値を表す上位二つの可能性は無効と定める。値0は偶数の $`y`$ 値を、値1は奇数の $`y`$ 値を表す。

次の条件がすべて真でない限り、ECDSA署名は無効であると定める。

<span id="eq-312"></span><span id="eq-313"></span><span id="eq-314"></span>

```math
\begin{aligned}
0 < {r} &< \mathtt{secp256k1n} & \qquad \text{(312)} \\
0 < {s} &< \mathtt{secp256k1n} \div 2 + 1 & \qquad \text{(313)} \\
v &\in \{0,1\} & \qquad \text{(314)}
\end{aligned}
```

ここで、

<span id="eq-315"></span>

```math
\begin{aligned}
\mathtt{secp256k1n} &= 115792089237316195423570985008687907852837564279074904382605163141518161494337 & \qquad \text{(315)}
\end{aligned}
```

$`s`$ に対するこの制限は、 $`\Xi_{\mathtt{ECREC}}`$ プリコンパイルの制限 [212](appendix-e-precompiled-contracts.md#eq:ecrec_precompile_validity) より厳しいことに注意されたい。詳細は [(Buterin 2015)](../references.md#ref-EIP-2) によるEIP-2を参照されたい。

所与の秘密鍵 $`p_{\mathrm{r}}`$ に対応するEthereumアドレス $`A(p_{\mathrm{r}})`$ （160ビット値）は、対応するECDSA公開鍵のKeccak-256ハッシュの右端160ビットとして定義される。

<span id="eq-316"></span>

```math
A(p_{\mathrm{r}}) = \mathcal{B}_{96..255}\big(\mathtt{KEC}\big( \mathtt{ECDSAPUBKEY}(p_{\mathrm{r}}) \big) \big) \qquad \text{(316)}
```

<div id="h_of_T">

</div>

署名対象のメッセージ・ハッシュ $`h(T)`$ は、トランザクションのKeccak-256ハッシュである。四種類の署名方式が利用できる。

<span id="eq-317"></span><span id="eq-318"></span>

```math
\begin{aligned}
L_{\mathrm{X}}(T) & \equiv & \begin{cases}
(T_{\mathrm{n}}, T_{\mathrm{p}}, T_{\mathrm{g}}, T_{\mathrm{t}}, T_{\mathrm{v}}, \mathbf{p}) & \text{if} \; T_{\mathrm{x}} = 0 \land T_{\mathrm{w}} \in \{27, 28\} \\
(T_{\mathrm{n}}, T_{\mathrm{p}}, T_{\mathrm{g}}, T_{\mathrm{t}}, T_{\mathrm{v}}, \mathbf{p}, \beta, (), ()) & \text{if} \; T_{\mathrm{x}} = 0 \land T_{\mathrm{w}} \in \{2\beta + 35, 2\beta + 36\} \\
(T_{\mathrm{c}}, T_{\mathrm{n}}, T_{\mathrm{p}}, T_{\mathrm{g}}, T_{\mathrm{t}}, T_{\mathrm{v}}, \mathbf{p}, T_{\mathbf{A}}) & \text{if} \; T_{\mathrm{x}} = 1 \\
(T_{\mathrm{c}}, T_{\mathrm{n}}, T_{\mathrm{f}}, T_{\mathrm{m}},  T_{\mathrm{g}}, T_{\mathrm{t}}, T_{\mathrm{v}}, \mathbf{p}, T_{\mathbf{A}}) & \text{if} \; T_{\mathrm{x}} = 2
\end{cases} & \qquad \text{(317)} \\
\text{where} \\
\mathbf{p} & \equiv & \begin{cases}
T_{\mathbf{i}} & \text{if}\ T_{\mathrm{t}} = \varnothing \\
T_{\mathbf{d}} & \text{otherwise}
\end{cases} \\
h(T) & \equiv & \begin{cases}
\mathtt{KEC}( \mathtt{RLP}(L_{\mathrm{X}}(T)) ) & \text{if} \; T_{\mathrm{x}} = 0 \\
\mathtt{KEC}( T_{\mathrm{x}} \cdot \mathtt{RLP}(L_{\mathrm{X}}(T)) ) & \text{otherwise}
\end{cases} & \qquad \text{(318)}
\end{aligned}
```

署名済みトランザクション $`G(T, p_{\mathrm{r}})`$ を次のように定義する。

<span id="eq-319"></span><span id="eq-320"></span>

```math
\begin{aligned}
G(T, p_{\mathrm{r}}) \equiv T \quad \text{except:} & \qquad \text{(319)} \\
(T_{\mathrm{y}}, T_{\mathrm{r}}, T_{\mathrm{s}}) = \mathtt{ECDSASIGN}(h(T), p_{\mathrm{r}}) & \qquad \text{(320)}
\end{aligned}
```

[前述の内容を繰り返すと](../chapters/04-blocks-state-transactions.md#T__r_T__s)、

<span id="eq-321"></span><span id="eq-322"></span>

```math
\begin{aligned}
{T_{\mathrm{r}}} = r & \qquad \text{(321)} \\
{T_{\mathrm{s}}} = s & \qquad \text{(322)}
\end{aligned}
```

であり、レガシー・トランザクションの $`T_{\mathrm{w}}`$ は $`27 + T_{\mathrm{y}}`$ または $`2\beta + 35 + T_{\mathrm{y}}`$ のいずれかである。

これにより、トランザクションの送信者関数 $`S`$ を次のように定義できる。

<span id="eq-323"></span><span id="eq-324"></span>

```math
\begin{aligned}
S(T) &\equiv& \mathcal{B}_{96..255}\big(\mathtt{KEC}\big( \mathtt{ECDSARECOVER}(h(T), v, T_{\mathrm{r}}, T_{\mathrm{s}}) \big) \big) & \qquad \text{(323)} \\
v &\equiv& \begin{cases}
T_{\mathrm{w}} - 27 & \text{if} \; T_{\mathrm{x}} = 0 \land T_{\mathrm{w}} \in \{27, 28\} \\
(T_{\mathrm{w}}-35) \bmod 2 & \text{if} \ T_{\mathrm{x}} = 0 \land T_{\mathrm{w}} \in \{2\beta + 35, 2\beta + 36\} \\
T_{\mathrm{y}} & \text{if} \ T_{\mathrm{x}} = 1 \lor T_{\mathrm{x}} = 2
\end{cases} & \qquad \text{(324)}
\end{aligned}
```

署名済みトランザクションの送信者が署名者のアドレスに等しいという主張は自明であろう。

<span id="eq-325"></span>

```math
\forall T: \forall p_{\mathrm{r}}: S(G(T, p_{\mathrm{r}})) \equiv A(p_{\mathrm{r}}) \qquad \text{(325)}
```
