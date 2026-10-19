[分割版目次](../README.md) | [前へ](11-blocktree-to-blockchain.md) | [次へ](13-contract-implementation.md) | [単一ページ版](../../ethereum_yellow_paper_ja.md)

<span id="ch:finalisation"></span>

# 12. ブロックの最終化

ブロックの最終化処理には次の3段階がある。

1.  引き出しを実行する。

2.  トランザクションを検証する。

3.  状態を検証する。

## 12.1. 引き出しの実行

ブロックのトランザクションを処理した後、引き出しを実行する。引き出しとは、受取人アカウントの残高を指定された Gwei 量だけ増やすことにすぎない。ほかの残高は減少せず、引き出しは移転ではなく資金の創出である。引き出し操作は失敗せず、gas コストもない。関数 $`E`$ を引き出し状態遷移関数として定義する。

<span id="eq-177"></span><span id="eq-178"></span><span id="eq-179"></span>

```math
\begin{aligned}
E(\boldsymbol{\sigma}_w, W) & \equiv & \boldsymbol{\sigma}_{w+1} & \qquad \text{(177)} \\
\boldsymbol{\sigma}_{w+1} & \equiv & \boldsymbol{\sigma}_w \quad \text{except:} & \qquad \text{(178)} \\
\boldsymbol{\sigma}_{w+1}[W_r]_{\mathrm{b}} & \equiv & \boldsymbol{\sigma}_{w}[W_r]_{\mathrm{b}} + (W_a \times 10^9) & \qquad \text{(179)}
\end{aligned}
```

<div id="Kappa">

</div>

最後に、引き出しに対するブロック水準の状態遷移関数 $`K`$ を定義する。

<span id="eq-180"></span>

```math
K(\boldsymbol{\sigma}, B) \equiv E(E(\boldsymbol{\sigma}, W_0), W_1) ... \qquad \text{(180)}
```

## 12.2. トランザクションの検証

与えられた **gasUsed** は、列挙されたトランザクションと正確に対応しなければならない。ブロック内の総使用gas $`{B_{\mathrm{H}}}_{\mathrm{g}}`$[↗](04-blocks-state-transactions.md#H__g) は、最後のトランザクション時点の累積使用gasに等しくなければならない。

<span id="eq-181"></span>

```math
{B_{\mathrm{H}}}_{\mathrm{g}} = \ell(\mathbf{R})_{\mathrm{u}} \qquad \text{(181)}
```

<span id="sec:statenoncevalidation"></span>

## 12.3. 状態の検証

<div id="Gamma">

</div>

ここで、ブロック $`B`$ をその初期状態へ写す関数 $`\Gamma`$ を定義できる。

<span id="eq-182"></span>

```math
\Gamma(B) \equiv \begin{cases}
\boldsymbol{\sigma}_0 & \text{if} \quad P(B_{\mathrm{H}}) = \varnothing \\
\boldsymbol{\sigma}_{\mathrm{i}}: \mathtt{TRIE}(L_{\mathrm{S}}(\boldsymbol{\sigma}_{\mathrm{i}})) = {P(B_{\mathrm{H}})_{\mathrm{H}}}_{\mathrm{r}} & \text{otherwise}
\end{cases} \qquad \text{(182)}
```

ここで $`\mathtt{TRIE}(L_{\mathrm{S}}(\boldsymbol{\sigma}_{\mathrm{i}}))`$ は状態 $`\boldsymbol{\sigma}_{\mathrm{i}}`$ のトライのルート・ノード・ハッシュを意味する。トライは本質的に不変データ構造であるため、実装はこれを状態データベースに格納すると仮定する。この格納は自明かつ効率的である。

<div id="Phi">

</div>

最後に、不完全なブロック $`B`$ を完全なブロック $`B'`$ へ写すブロック遷移関数 $`\Phi`$ を定義する。

<span id="eq-183"></span><span id="eq-184"></span>

```math
\begin{aligned}
\Phi(B) & \equiv & B': \quad B' = B \quad \text{except:} & \qquad \text{(183)} \\
{B'_{\mathrm{H}}}_{\mathrm{r}} & = & \mathtt{TRIE}(L_{\mathrm{S}}(K(\Pi(\Gamma(B), B), B))) & \qquad \text{(184)}
\end{aligned}
```

本稿の冒頭で述べたように、$`\Pi`$[↗](#Pi) は状態遷移関数であり、トランザクション評価関数 $`\Upsilon`$[↗](02-blockchain-paradigm.md#Upsilon_state_transition) によって定義される。

前述のとおり、 $`\mathbf{R}[n]_{\mathrm{z}}`$ 、 $`\mathbf{R}[n]_{\mathbf{l}}`$ 、 $`\mathbf{R}[n]_{\mathrm{u}}`$ は、それぞれ第 $`n`$ トランザクション後のステータス・コード、ログ、累積使用gasである（タプルの第4要素 $`\mathbf{R}[n]_{\mathrm{b}}`$ は、すでにログによって定義した）。また第 $`n`$ 状態 $`\boldsymbol{\sigma}[n]`$ を、直前のトランザクションから得られた状態（最初のトランザクションではブロックの初期状態）に対応するトランザクションを適用して得られる状態として単純に定義する。

<span id="eq-185"></span><span id="sigma_n"></span>

```math
\boldsymbol{\sigma}[n] = \begin{cases} \Gamma(B) & \text{if} \quad n < 0 \\ \Upsilon(\boldsymbol{\sigma}[n - 1], B_{\mathbf{T}}[n]) & \text{otherwise} \end{cases} \qquad \text{(185)}
```

$`B_{\mathbf{R}}[n]_{\mathrm{u}}`$ についても同様の方法を採り、各項目を、対応するトランザクションの評価に使用したgasと直前の項目（最初の場合はゼロ）との和として定義し、累計値を得る。

<span id="eq-186"></span>

```math
\mathbf{R}[n]_{\mathrm{u}} = \begin{cases} 0 & \text{if} \quad n < 0 \\
\begin{array}{l}
\Upsilon^g(\boldsymbol{\sigma}[n - 1], B_{\mathbf{T}}[n])\\ \quad + \mathbf{R}[n-1]_{\mathrm{u}}
\end{array}
 & \text{otherwise} \end{cases} \qquad \text{(186)}
```

$`\mathbf{R}[n]_{\mathbf{l}}`$ については、トランザクション実行関数で定義した $`\Upsilon^{\mathbf{l}}`$[↗](06-transaction-execution.md#Upsilon_pow_l) 関数を用いる。

<span id="eq-187"></span>

```math
\mathbf{R}[n]_{\mathbf{l}} =
\Upsilon^{\mathbf{l}}(\boldsymbol{\sigma}[n - 1], B_{\mathbf{T}}[n]) \qquad \text{(187)}
```

$`\mathbf{R}[n]_{\mathrm{z}}`$[↗](06-transaction-execution.md#Upsilon_pow_z) も同様に定義する。

<span id="eq-188"></span>

```math
\mathbf{R}[n]_{\mathrm{z}} =
\Upsilon^{\mathrm{z}}(\boldsymbol{\sigma}[n - 1], B_{\mathbf{T}}[n]) \qquad \text{(188)}
```

<div id="Pi">

</div>

最後に、 $`\Pi`$ を最終トランザクションの結果状態 $`\ell(\boldsymbol{\sigma})`$ として定義する。

<span id="eq-189"></span>

```math
\Pi(\boldsymbol{\sigma}, B) \equiv \ell(\boldsymbol{\sigma}) \qquad \text{(189)}
```

以上により、（合意形成前の）完全なブロック遷移機構が定義された。
