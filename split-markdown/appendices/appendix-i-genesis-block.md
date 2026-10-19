[分割版目次](../README.md) | [前へ](appendix-h-virtual-machine.md) | [次へ](appendix-j-ethash.md) | [単一ページ版](../../ethereum_yellow_paper_ja.md)

<span id="app:genesis"></span>

# 付録I. ジェネシス・ブロック

<div id="Genesis_Block">

</div>

ジェネシス・ブロックは15項目からなり、次のように規定される。

<span id="eq-333"></span>

```math
\big( \big( 0_{256}, \mathtt{KEC}\big(\mathtt{RLP}\big( () \big)\big), 0_{160}, stateRoot, 0, 0, 0_{2048}, 2^{34}, 0, 0, 3141592, time, 0, 0_{256},  \mathtt{KEC}\big( (42) \big) \big), (), () \big) \qquad \text{(333)}
```

ここで $`0_{256}`$ は、すべてゼロである256ビット・ハッシュの親ハッシュを指す。 $`0_{160}`$ は、すべてゼロである160ビット・ハッシュの受益者アドレスを指す。 $`0_{2048}`$ は、2048ビットすべてがゼロであるログ・ブルームを指す。 $`2^{34}`$ はdifficultyを指す。トランザクション・トライ・ルート、レシート・トライ・ルート、使用gas、ブロック番号、extraDataはいずれも $`0`$ であり、空バイト配列と等価である。ommer列とトランザクション列はいずれも空であり、 $`()`$ で表す。 $`\mathtt{KEC}\big( (42) \big)`$ は、nonceに用いる、最初で唯一のバイトの値が42である長さ1のバイト配列のKeccak-256ハッシュを指す。 $`\mathtt{KEC}\big(\mathtt{RLP}\big( () \big)\big)`$ の値は、RLPにおけるommerリストのハッシュを指し、両者とも空リストである。

概念実証版の系列には開発用プレマインが含まれるため、状態ルート・ハッシュはある値 $`stateRoot`$ となる。また $`time`$ にはジェネシス・ブロックの初期タイムスタンプが設定される。これらの値については最新の文書を参照されたい。
