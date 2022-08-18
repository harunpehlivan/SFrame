
import _ast

def dont_visit(self, node):
    pass

def visit_children(self, node):
    for child in self.children(node):
        self.visit(child)


class Visitor(object):

    def children(self, node):
        for field in node._fields:
            value = getattr(node, field)
            if isinstance(value, (list, tuple)):
                for item in value:
                    if isinstance(item, _ast.AST):
                        yield item
            elif  isinstance(value, _ast.AST):
                yield value

        return



    def visit_list(self, nodes, *args, **kwargs):

        return [self.visit(node, *args, **kwargs) for node in nodes]

    def visit(self, node, *args, **kwargs):
        node_name = type(node).__name__

        attr = f'visit{node_name}'

        if hasattr(self, attr) or not hasattr(self, 'visitDefault'):
            mehtod = getattr(self, f'visit{node_name}')
        else:
            mehtod = getattr(self, 'visitDefault')
        return mehtod(node, *args, **kwargs)



class Mutator(Visitor):
    
    def mutateDefault(self, node):
        for field in node._fields:
            value = getattr(node, field)
            if isinstance(value, (list, tuple)):
                for i, item in enumerate(value):
                    if isinstance(item, _ast.AST):
                        new_item = self.mutate(item)
                        if new_item is not None:
                            value[i] = new_item
            elif  isinstance(value, _ast.AST):
                new_value = self.mutate(value)
                if new_value is not None:
                    setattr(node, field, new_value)

        return None
    
    def mutate(self, node, *args, **kwargs):

        node_name = type(node).__name__

        attr = f'mutate{node_name}'

        if hasattr(self, attr) or not hasattr(self, 'mutateDefault'):
            mehtod = getattr(self, f'mutate{node_name}')
        else:
            mehtod = getattr(self, 'mutateDefault')
        return mehtod(node, *args, **kwargs)

