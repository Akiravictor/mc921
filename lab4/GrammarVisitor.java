import java.util.*;


public class GrammarVisitor extends gramaticaBaseVisitor<Integer> {
	
	HashMap<String, String> declarationsType = new HashMap<String, String>();
	HashMap<String, Integer> numDeParametros = new HashMap<String, Integer>();
	List<String> argListDefined = new ArrayList<>();
	
	@Override public Integer visitDeclara(gramaticaParser.DeclaraContext ctx) {
		String IDname = ctx.ID().getText();

		declarationsType.put(IDname, "var");

		visit(ctx.expressao());
		return 0;
	}
}
