import java.util.*;


public class GrammarVisitor extends gramaticaBaseVisitor<Integer> {
	
	HashMap<String, String> declarationsType = new HashMap<String, String>();
	HashMap<String, Integer> numDeParametros = new HashMap<String, Integer>();
	List<String> argListDefined = new ArrayList<>();
	
	@Override public Integer visitDeclara(gramaticaParser.DeclaraContext ctx) {
		String IDname = ctx.ID().getText();
		if(declarationsType.containsKey(IDname)){
			System.out.println("Symbol already declared: " + IDname);
		}
		else{
			declarationsType.put(IDname, "var");
		}
		visit(ctx.expressao());
		return 0;
	}

	@Override public Integer visitDefine(gramaticaParser.DefineContext ctx) {
		String IDname = ctx.ID().getText();
		if(declarationsType.containsKey(IDname)){
			System.out.println("Symbol already declared: " + IDname);
		}
		else{
			declarationsType.put(IDname, "func");
			numDeParametros.put(IDname, visit(ctx.argumentos()));
			//System.out.println("argListDefined: "+argListDefined);//@deBug
		}
		HashMap<String, String> declarationsTypeBackup = new HashMap<String, String>();
		argListDefined.forEach((nome)->{
			if(declarationsType.containsKey(nome)){
				declarationsTypeBackup.put(nome, declarationsType.get(nome));
				declarationsType.remove(nome);
			}
			declarationsType.put(nome, "var");
		});//java8
		visit(ctx.expressao());
		argListDefined.forEach((nome)-> declarationsType.remove(nome));//java8
		declarationsTypeBackup.forEach((nome,tipo) -> declarationsType.put(nome,tipo));//java8
		argListDefined.clear();
		return 0;
	}

	@Override public Integer visitPrimeiroArg(gramaticaParser.PrimeiroArgContext ctx) {
		argListDefined.add(ctx.ID().getText());
		return 1;
	}

	@Override public Integer visitExpandeArg(gramaticaParser.ExpandeArgContext ctx) {
		argListDefined.add(ctx.ID().getText());
		return 1 + visit(ctx.argumentos());
	}

	@Override public Integer visitPrimeiroParam(gramaticaParser.PrimeiroParamContext ctx) {
		return 1;
	}

	@Override public Integer visitExpandeParam(gramaticaParser.ExpandeParamContext ctx) {
		return 1 + visit(ctx.parametros());
	}

	@Override public Integer visitChamada(gramaticaParser.ChamadaContext ctx)  {
		String funcName = ctx.ID().getText();
		if(!declarationsType.containsKey(funcName))
			System.out.println("Symbol undeclared: "+funcName);
		else if(declarationsType.get(funcName) != "func")
				System.out.println("Bad used symbol: "+funcName);
		else if(visit(ctx.parametros()) != numDeParametros.get(funcName))
				System.out.println("Bad argument count: "+funcName);
		return 0;
	}

	@Override public Integer visitConstanteId(gramaticaParser.ConstanteIdContext ctx) {
		String nomeDaConstante = ctx.ID().getText();
		if(!declarationsType.containsKey(nomeDaConstante))
			System.out.println("Symbol undeclared: " + nomeDaConstante);
		else if(declarationsType.get(nomeDaConstante) != "var")
				System.out.println("Bad used symbol: "+nomeDaConstante);
		return 0;
	}
}
