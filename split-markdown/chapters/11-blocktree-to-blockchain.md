[分割版目次](../README.md) | [前へ](10-proof-of-stake-transition.md) | [次へ](12-block-finalisation.md) | [単一ページ版](../../ethereum_yellow_paper_ja.md)

<span id="ch:blocktree_to_blockchain"></span>

# 11. ブロック木からブロックチェーンへ

*Paris* ハードフォークでプルーフ・オブ・ステークへ移行する以前、正準ブロックチェーンは、[第10節](10-proof-of-stake-transition.md#ch:pos_transition)で $`B_{\mathrm{t}}`$ として定義した*総難易度*が最大のブロック経路と定義されていた。

[第10節](10-proof-of-stake-transition.md#ch:pos_transition)で記述した*終端ブロック*への到達後は、最大*総難易度*規則を廃止し、*LMD GHOST* と呼ばれる規則を採用しなければならない[^12]。

*Paris* 後にどのブロックが正準 Ethereum ブロックチェーンを構成するかを決定するには、本稿で記述しない Beacon Chain の追加情報が必要であることに注意されたい。Beacon Chain が発行するイベントを接頭辞 $`\mathtt{POS\_}`$ で表す。

[第10節](10-proof-of-stake-transition.md#ch:pos_transition)で述べた*遷移ブロック*における最初のイベントを起点として、 $`\mathtt{POS\_FORKCHOICE\_UPDATED}`$ イベントが発生するたびに、正準チェーンはジェネシス・ブロックから始まり、そのイベントがチェーン先頭として指定したブロックで終わるチェーンとして定義される。

$`\mathtt{POS\_FORKCHOICE\_UPDATED}`$ が発行された場合、かつその場合に限りチェーンの先頭を更新し、そのイベントが指定するブロックへ設定する。チェーン先頭を楽観的に更新してはならない。

$`\mathtt{POS\_FORKCHOICE\_UPDATED}`$ イベントはさらに最終化済みブロックを参照する。最新の最終化済みブロックをこのブロックに設定する。

正準ブロックチェーンは、[第10節](10-proof-of-stake-transition.md#ch:pos_transition)で定義した*終端ブロック*のハッシュと番号を持つブロックも含まなければならない。

[^12]: *LMD GHOST* は「Latest Message Driven」と「Greedy Heaviest-Observed Sub-Tree」という二つの頭字語からなる。
