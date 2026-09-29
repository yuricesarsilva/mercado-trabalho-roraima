-- Converte marcadores inseridos por build_docx.py em estilos/elementos do Word.
local styles = {
  COVERTITLE = 'Title',
  COVERAUTHOR = 'Author',
  COVERHEAD = 'Cover Heading',
  COVERTEXT = 'Cover Text',
  FLOATNOTE = 'Float Note',
}

local pagebreak = pandoc.RawBlock('openxml',
  '<w:p><w:r><w:br w:type="page"/></w:r></w:p>')

function Para(el)
  local first = el.content[1]
  if not first or first.t ~= 'Str' then return nil end
  local tag = first.text
  if tag == 'PAGEBREAKHERE' then return pagebreak end
  if tag == 'REFSHERE' then return pandoc.Div({}, {id = 'refs'}) end
  local style = styles[tag]
  if style then
    local inl = el.content
    inl:remove(1)
    if inl[1] and (inl[1].t == 'Space' or inl[1].t == 'SoftBreak') then inl:remove(1) end
    return pandoc.Div({pandoc.Para(inl)}, {['custom-style'] = style})
  end
end
