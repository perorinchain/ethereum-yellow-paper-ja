-- Preserve the original structure and distinguish translation additions.
-- Keep the title/front matter and portable tables usable in both editions.

local latex = FORMAT:match('latex') ~= nil
local translator_heading = '訳注（日本語訳で追加）'

function Math(element)
  if element.mathtype == 'InlineMath'
      and element.text:sub(1, 1) == '`'
      and element.text:sub(-1) == '`' then
    element.text = element.text:sub(2, -2)
  end
  return element
end

function CodeBlock(element)
  if element.classes:includes('math') then
    return pandoc.Para({pandoc.Math('DisplayMath', element.text)})
  end
end

function Header(element)
  local title = pandoc.utils.stringify(element.content)
  if element.level == 1 and title:match('^Ethereum：') then
    element.classes:insert('unlisted')
  elseif title == translator_heading then
    -- This is translation apparatus, not another original section/appendix.
    element.classes:insert('unlisted')
    element.classes:insert('unnumbered')
    element.identifier = 'translator-notes-heading'
  end
  return element
end

function Link(element)
  local number = element.target:match('^#tn%-(%d+)$')
  if number then
    element.classes:insert('translator-note-ref')
    element.attributes['role'] = 'doc-noteref'
    element.attributes['aria-label'] = '日本語訳で追加した訳注' .. number
    -- A normal link in superscript does not consume a Pandoc Note number.
    return pandoc.Superscript({element})
  end
  if element.target:match('^#tnref%-%d+$') then
    element.classes:insert('translator-note-back')
    element.attributes['role'] = 'doc-backlink'
    return element
  end
end

function Div(element)
  if latex and element.classes:includes('title-block') then
    local blocks = pandoc.List({pandoc.RawBlock('latex', '\\begin{center}')})
    blocks:extend(element.content)
    blocks:insert(pandoc.RawBlock('latex', '\\end{center}'))
    return blocks
  end
end

function Table(element)
  if #element.colspecs ~= 5 or #element.head.rows == 0 then
    return nil
  end
  local cells = element.head.rows[1].cells
  if pandoc.utils.stringify(cells[1].contents) ~= '値'
      or pandoc.utils.stringify(cells[2].contents) ~= 'ニーモニック' then
    return nil
  end
  element.classes:insert('evm-instructions')
  -- The instruction description contains nearly all prose and formulae.
  local widths = {0.07, 0.18, 0.04, 0.04, 0.67}
  local specifications = element.colspecs
  for index, width in ipairs(widths) do
    specifications[index][2] = width
  end
  element.colspecs = specifications
  return element
end

function Pandoc(document)
  if not latex then
    return nil
  end
  local blocks = pandoc.List()
  local title_removed = false
  local contents_inserted = false
  for _, block in ipairs(document.blocks) do
    if not title_removed and block.t == 'Header' and block.level == 1 then
      -- The standalone template already emits this title via \maketitle.
      document.meta.title = pandoc.MetaInlines(block.content)
      title_removed = true
    else
      blocks:insert(block)
      if block.t == 'Div' and block.classes:includes('translation-notice') then
        blocks:insert(pandoc.RawBlock('latex',
          '\\clearpage\n{\\setcounter{tocdepth}{3}\\tableofcontents}\n\\clearpage'))
        contents_inserted = true
      end
    end
  end
  if not contents_inserted then
    error('the translation notice is missing; cannot place the contents')
  end
  document.blocks = blocks
  return document
end
